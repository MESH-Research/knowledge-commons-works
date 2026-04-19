#! /bin/bash

# Color variables
red='\033[0;31m'
green='\033[0;32m'
yellow='\033[0;33m'
blue='\033[0;34m'
magenta='\033[0;35m'
cyan='\033[0;36m'
# Clear the color after that
clear='\033[0m'

echo -e "${yellow}Building assets for Knowledge Commons Works instance...${clear}"

# All `invenio webpack ...` calls below are bundler-/package-manager-agnostic:
# they delegate to whichever project + npm package class are configured in
# invenio.cfg via WEBPACKEXT_PROJECT and WEBPACKEXT_NPM_PKG_CLS. KCWorks sets
#   WEBPACKEXT_PROJECT      = "invenio_assets.webpack:rspack_project"
#   WEBPACKEXT_NPM_PKG_CLS  = "pynpm.package:PNPMPackage"
# so create/install/build run against the rspack scaffold and shell out to
# pnpm (PNPMPackage hard-codes npm_bin="pnpm" and uses --shamefully-hoist).
# We intentionally do NOT replicate invenio_cli's js_pkg_man.env_overrides()
# wrapper — those env vars only matter when subprocesses pick up the package
# manager from $PATH/env; PNPMPackage invokes pnpm directly via subprocess.

echo -e "${yellow}Collecting static files...${clear}"
invenio collect -v
echo -e "${yellow}Building assets...${clear}"
invenio webpack clean create
invenio webpack install
cd /opt/invenio/src
invenio shell ./scripts/symlink_assets.py
invenio webpack build
echo -e "${green}All done building assets...${clear}"