#!/usr/bin/env python3
"""Script to clear stuck invenio-stats-dashboard task locks.

This script connects to the same Redis cache that invenio-stats-dashboard uses
and manually removes the stuck lock keys that prevent aggregation tasks from running.

Usage:
    python clear_stats_lock.py [--lock-name LOCK_NAME] [--dry-run]

Examples:
    python clear_stats_lock.py  # Clear default aggregation lock
    python clear_stats_lock.py --lock-name community_stats_cache_generation  # Clear cache generation lock
    python clear_stats_lock.py --dry-run  # Show what would be cleared without actually clearing
"""

import argparse
import sys

try:
    from flask import Flask
    from invenio_app import create_app
    from invenio_cache import current_cache
except ImportError as e:
    print(f"Error: Could not import required modules: {e}")
    print("Make sure you're running this script from within your InvenioRDM environment")
    print("and that invenio-stats-dashboard is installed.")
    sys.exit(1)


def clear_lock(lock_name: str, dry_run: bool = False) -> bool:
    """Clear a specific lock from the cache.
    
    Args:
        lock_name: The name of the lock to clear (without 'lock:' prefix)
        dry_run: If True, only show what would be cleared without actually clearing
        
    Returns:
        True if successful, False otherwise
    """
    full_lock_key = f"lock:{lock_name}"
    
    try:
        # Check if the lock exists
        current_value = current_cache.get(full_lock_key)
        
        if current_value is None:
            print(f"ℹ️  Lock '{full_lock_key}' not found (already cleared or never existed)")
            return True
            
        print(f"🔍 Found lock '{full_lock_key}' with value: {current_value}")
        
        if dry_run:
            print(f"🔍 DRY RUN: Would clear lock '{full_lock_key}'")
            return True
            
        # Clear the lock
        success = current_cache.delete(full_lock_key)
        
        if success:
            print(f"✅ Successfully cleared lock '{full_lock_key}'")
            return True
        else:
            print(f"❌ Failed to clear lock '{full_lock_key}'")
            return False
            
    except Exception as e:
        print(f"❌ Error clearing lock '{full_lock_key}': {e}")
        return False


def list_all_locks() -> None:
    """List all lock keys in the cache."""
    try:
        # Get all keys that start with 'lock:'
        all_keys = current_cache.cache._read_client.keys("lock:*")
        
        if not all_keys:
            print("ℹ️  No lock keys found in cache")
            return
            
        print(f"🔍 Found {len(all_keys)} lock keys:")
        for key in all_keys:
            # Decode bytes to string if needed
            if isinstance(key, bytes):
                key = key.decode('utf-8')
            value = current_cache.get(key)
            print(f"  - {key}: {value}")
            
    except Exception as e:
        print(f"❌ Error listing locks: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Clear stuck invenio-stats-dashboard task locks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clear_stats_lock.py                                    # Clear default aggregation lock
  python clear_stats_lock.py --lock-name community_stats_cache_generation  # Clear cache generation lock
  python clear_stats_lock.py --list-locks                      # List all locks
  python clear_stats_lock.py --dry-run                         # Show what would be cleared
        """
    )
    
    parser.add_argument(
        "--lock-name",
        default="community_stats_aggregation",
        help="Name of the lock to clear (default: community_stats_aggregation)"
    )
    
    parser.add_argument(
        "--list-locks",
        action="store_true",
        help="List all lock keys in the cache"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be cleared without actually clearing"
    )
    
    args = parser.parse_args()
    
    print("🚀 Starting invenio-stats-dashboard lock clearing script")
    print("=" * 60)
    
    try:
        # Create Flask app context
        app = create_app()
        
        with app.app_context():
            if args.list_locks:
                list_all_locks()
                return
                
            success = clear_lock(args.lock_name, args.dry_run)
            
            if success:
                print("\n✅ Lock clearing completed successfully!")
                print("You should now be able to run aggregation tasks again.")
            else:
                print("\n❌ Lock clearing failed!")
                print("Check your Redis connection and try again.")
                sys.exit(1)
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you're running this script from within your InvenioRDM environment")
        sys.exit(1)


if __name__ == "__main__":
    main()
