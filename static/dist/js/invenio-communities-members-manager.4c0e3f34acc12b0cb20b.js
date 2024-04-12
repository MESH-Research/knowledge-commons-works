"use strict";(self.webpackChunkinvenio_assets=self.webpackChunkinvenio_assets||[]).push([[8249],{8299:(e,t,n)=>{var r=n(64467),o=n(86763),i=n(53196),l=n(5905),a=n(14673),c=n(15094),s=n(62660),u=n(12152),m=n(23029),d=n(92901),p=n(56822),b=n(53954),y=n(85501),f=n(96540),h=n(5556),v=n.n(h),A=n(61234),C=n(10739),E=n(98871),O=n(25315),g=n(28803);function S(e,t,n){return t=(0,b.A)(t),(0,p.A)(e,k()?Reflect.construct(t,n||[],(0,b.A)(e).constructor):t.apply(e,n))}function k(){try{var e=!Boolean.prototype.valueOf.call(Reflect.construct(Boolean,[],(function(){})))}catch(e){}return(k=function(){return!!e})()}var R=function(e){function t(){return(0,m.A)(this,t),S(this,t,arguments)}return(0,y.A)(t,e),(0,d.A)(t,[{key:"render",value:function(){var e=this.props,t=e.config,n=e.roles,r=e.rolesCanInvite,o=e.community,i=e.communityGroupsEnabled,a=e.appName,c=new A.C(n).getMembersFilters();return f.createElement(f.Fragment,null,f.createElement("div",{className:"auto-column-grid"},f.createElement("div",null,f.createElement("div",{className:"mobile only rel-mb-1"},f.createElement(O.J,{community:o},f.createElement(g.Z,{rolesCanInvite:r,groupsEnabled:i,community:o}))),f.createElement(E.IW,{fluid:!0})),f.createElement("div",{className:"flex align-items-center column-mobile"},f.createElement("div",{className:"tablet only"},f.createElement(O.J,{community:o},f.createElement(g.Z,{rolesCanInvite:r,groupsEnabled:i,community:o}))),f.createElement("div",{className:"full-width flex align-items-center justify-end column-mobile"},f.createElement(l.i4,{customFilters:c}),f.createElement(E.FU,{values:t.sortOptions})))),f.createElement("div",{className:"rel-mb-1"},f.createElement(C.k,null)),f.createElement(l.s9,{layoutOptions:t.layoutOptions,appName:a}))}}])}(f.Component);R.propTypes={config:v().object.isRequired,roles:v().array.isRequired,rolesCanInvite:v().object.isRequired,community:v().object.isRequired,communityGroupsEnabled:v().bool.isRequired,appName:v().string},R.defaultProps={appName:""};var M=n(2685),j=n(1489),w=n(27041),x=n(76217),q=n(3487),N=n(38102);function P(e,t,n){return t=(0,b.A)(t),(0,p.A)(e,I()?Reflect.construct(t,n||[],(0,b.A)(e).constructor):t.apply(e,n))}function I(){try{var e=!Boolean.prototype.valueOf.call(Reflect.construct(Boolean,[],(function(){})))}catch(e){}return(I=function(){return!!e})()}var B=function(e){function t(){return(0,m.A)(this,t),P(this,t,arguments)}return(0,y.A)(t,e),(0,d.A)(t,[{key:"render",value:function(){var e=this.props,t=e.resetQuery,n=e.extraContent,r=e.queryString,o=e.community,i=e.communityGroupsEnabled,l=e.rolesCanInvite;return f.createElement(M.A.Group,null,f.createElement(M.A,{as:j.A,className:"computer only"},f.createElement(j.A.Column,{width:"13"}),f.createElement(j.A.Column,{width:"3"},f.createElement(O.J,{community:o},f.createElement(g.Z,{rolesCanInvite:l,groupsEnabled:i,community:o})))),f.createElement(M.A,{placeholder:!0,textAlign:"center"},f.createElement(w.A,{icon:!0},f.createElement(x.A,{name:"search"}),N.M.t("No matching members found.")),r&&f.createElement("p",null,f.createElement("em",null,N.M.t("Current search"),' "',r,'"')),f.createElement(q.A,{primary:!0,onClick:function(){return t()}},N.M.t("Clear query")),n))}}])}(f.Component);B.propTypes={resetQuery:v().func.isRequired,queryString:v().string.isRequired,rolesCanInvite:v().object.isRequired,community:v().object.isRequired,communityGroupsEnabled:v().bool.isRequired,extraContent:v().node},B.defaultProps={extraContent:null};var D=(0,E.Q2)(B),G=n(53959),J=n(80296),Q=n(10467),U=n(54756),T=n.n(U),H=n(80045),z=n(50363),_=n(34667),F=n(67844),V=n(71086),Z=n.n(V),L=["value"];function K(e,t,n){return t=(0,b.A)(t),(0,p.A)(e,W()?Reflect.construct(t,n||[],(0,b.A)(e).constructor):t.apply(e,n))}function W(){try{var e=!Boolean.prototype.valueOf.call(Reflect.construct(Boolean,[],(function(){})))}catch(e){}return(W=function(){return!!e})()}var X=function(e){function t(e){var n;(0,m.A)(this,t),n=K(this,t,[e]),(0,r.A)(n,"handleOnChange",(function(){var e=n.context,t=e.setAllSelected,r=e.allSelected;n.setState({allSelectedChecked:!r}),t(!r,!0)})),(0,r.A)(n,"handleActionOnChange",(function(e,t){var r=t.value;(0,H.A)(t,L);if(r){var o=n.props.optionSelectionCallback,i=n.context,l=i.selectedCount,a=i.bulkActionContext;o(r,Z()(a,(function(e){return!0===e.selected})),l)}}));var o=n.props.allSelected;return n.state={allSelectedChecked:o},n}return(0,y.A)(t,e),(0,d.A)(t,[{key:"componentDidMount",value:function(){var e=this.context.allSelected;this.setState({allSelectedChecked:e})}},{key:"render",value:function(){var e=this.props.bulkDropdownOptions,t=this.state.allSelectedChecked,n=this.context,r=n.allSelected,o=n.selectedCount,l=0===o,a=e.map((function(e){return{key:e.key,value:e.value,text:e.text,disabled:l}}));return f.createElement(i.default,{id:"InvenioCommunities.SearchResultsBulkActionsManager.layout"},f.createElement("div",{className:"flex"},f.createElement(z.A,{className:"align-self-center mr-10",onChange:this.handleOnChange,checked:t&&r,"aria-label":N.M.t("Select all members")}),f.createElement(_.A,{className:"align-self-center fluid-responsive",text:N.M.t("{{count}} members selected",{count:o}),options:a,"aria-label":N.M.t("bulk actions"),item:!0,selection:!0,value:null,selectOnBlur:!1,onChange:this.handleActionOnChange,selectOnNavigation:!1})))}}])}(f.Component);(0,r.A)(X,"contextType",F.X),X.propTypes={bulkDropdownOptions:v().array.isRequired,allSelected:v().bool,optionSelectionCallback:v().func.isRequired},X.defaultProps={allSelected:!1};i.default.component("SearchResultsBulkActions",X);var Y=n(29889),$=n(28626),ee=n(36704),te=n(11775),ne=n(73916),re=n.n(ne),oe=n(80501),ie=n(48423),le=n(52822),ae=n(81057);function ce(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function se(e,t,n){return t=(0,b.A)(t),(0,p.A)(e,ue()?Reflect.construct(t,n||[],(0,b.A)(e).constructor):t.apply(e,n))}function ue(){try{var e=!Boolean.prototype.valueOf.call(Reflect.construct(Boolean,[],(function(){})))}catch(e){}return(ue=function(){return!!e})()}var me=function(e){function t(e){var n;(0,m.A)(this,t),n=se(this,t,[e]),(0,r.A)(n,"bulkAction",(function(e){e()})),(0,r.A)(n,"handleChangeRole",(function(e){n.setState({role:e})})),(0,r.A)(n,"handleChangeVisibility",(function(e){n.setState({visible:"public"===e})})),(0,r.A)(n,"updateSelectedMembers",(function(e){n.setState({selectedMembers:e})})),(0,r.A)(n,"handleChooseCurrentAction",(function(e,t,o){var i=re()(t,(function(e){return function(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?ce(Object(n),!0).forEach((function(t){(0,r.A)(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):ce(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}({},e.data.member)}));n.updateSelectedMembers(i),n.setState({currentAction:e}),n.handleModalOpen()})),(0,r.A)(n,"handleModalClose",(function(){return n.setState({modalOpen:!1})})),(0,r.A)(n,"handleModalOpen",(function(){return n.setState({modalOpen:!0})})),(0,r.A)(n,"handleActionClick",(0,Q.A)(T().mark((function e(){var t,r,o,i,l,a,c,s;return T().wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return t=n.state.selectedMembers,r=n.props,o=r.updateQueryState,i=r.currentQueryState,l=n.context.setAllSelected,a=n.currentAction.action,c=n.state[n.currentAction.actionParam],s=Object.entries(t).map((function(e){var t=(0,J.A)(e,2);t[0];return t[1]})),n.setState({loading:!0}),n.cancellableAction=(0,ae.withCancel)(a(s,c)),e.prev=8,e.next=11,n.cancellableAction.promise;case 11:n.setState({loading:!1}),n.handleModalClose(),n.setState({role:void 0,visible:void 0}),o(i),l(!1,!0),e.next=23;break;case 18:if(e.prev=18,e.t0=e.catch(8),"UNMOUNTED"!==e.t0){e.next=22;break}return e.abrupt("return");case 22:n.setState({loading:!1,error:e.t0});case 23:case"end":return e.stop()}}),e,null,[[8,18]])}))));var o=n.props.community;return n.membersApi=new $.D(o),n.state={modalOpen:!1,currentAction:void 0,role:void 0,visible:void 0,selectedMembers:{}},n}return(0,y.A)(t,e),(0,d.A)(t,[{key:"componentWillUnmount",value:function(){this.cancellableAction&&this.cancellableAction.cancel()}},{key:"bulkActions",get:function(){var e=this,t=this.props,n=t.roles,r=t.visibilities,o=t.permissions;return[{key:1,value:"change_role",text:N.M.t("Change roles"),renderOnActive:function(){return f.createElement(oe.A,null,f.createElement(ee.Q,{options:n,label:N.M.t("Role"),onOptionChangeCallback:e.handleChangeRole,permissions:o}))},action:this.membersApi.bulkUpdateRoles,actionParam:"role"},{key:2,value:"change_visibility",text:N.M.t("Change visibilities"),action:this.membersApi.bulkUpdateVisibilities,actionParam:"visible",renderOnActive:function(){return f.createElement(oe.A,null,f.createElement(ee.Q,{options:r,label:N.M.t("Visibility"),onOptionChangeCallback:e.handleChangeVisibility,permissions:o}))}},{key:3,value:"remove_from_community",text:N.M.t("Remove from community"),action:this.membersApi.bulkRemoveMembers}]}},{key:"currentAction",get:function(){var e=this.state.currentAction;return this.bulkActions.find((function(t){return t.value===e}))}},{key:"render",value:function(){var e,t,n=this.state,r=n.modalOpen,o=n.selectedMembers,i=n.loading,l=n.error,a=Object.keys(o).length,c=(null===(e=this.currentAction)||void 0===e?void 0:e.renderOnActive)&&this.currentAction.renderOnActive(),s=null===(t=this.currentAction)||void 0===t?void 0:t.text,u=i||0===a||void 0===!this.state[this.currentAction.actionParam];return f.createElement(f.Fragment,null,f.createElement(X,{bulkDropdownOptions:this.bulkActions,optionSelectionCallback:this.handleChooseCurrentAction}),f.createElement(ie.A,{onClose:this.handleModalClose,onOpen:this.handleModalOpen,closeOnDimmerClick:!1,open:r,role:"dialog","aria-labelledby":"bulk-actions-modal-header"},f.createElement(ie.A.Header,{as:"h2",id:"bulk-actions-modal-header"},s),f.createElement(ie.A.Content,null,l&&f.createElement(Y.K,{error:l}),f.createElement(te.r,{updateSelectedMembers:this.updateSelectedMembers,selectedMembers:o}),c),f.createElement(ie.A.Actions,null,f.createElement(q.A,{content:N.M.t("Cancel"),labelPosition:"left",icon:"cancel",loading:i,disabled:i,floated:"left",onClick:this.handleModalClose}),f.createElement(le.x,{key:"communityInviteMembersSelected",count:a},"You have selected ",{selectedCount:a}," users"),f.createElement(q.A,{content:s,labelPosition:"left",loading:i,disabled:u,icon:"checkmark",primary:!0,onClick:this.handleActionClick}))))}}])}(f.Component);(0,r.A)(me,"contextType",F.X),me.propTypes={community:v().object.isRequired,roles:v().array.isRequired,visibilities:v().array.isRequired,permissions:v().object.isRequired,updateQueryState:v().func.isRequired,currentQueryState:v().object.isRequired};var de=(0,E.Q2)(me),pe=function(e){var t=e.results,n=e.community,r=e.communityGroupsEnabled,o=e.rolesCanInvite,i=e.config;return f.createElement(G.A,null,f.createElement(G.A.Header,null,f.createElement(G.A.Row,null,f.createElement(G.A.HeaderCell,{width:6},f.createElement(de,{community:n,roles:i.roles,visibilities:i.visibility,permissions:i.permissions})),f.createElement(G.A.HeaderCell,{width:3},N.M.t("Member since")),f.createElement(G.A.HeaderCell,{width:3},N.M.t("Visibility")),f.createElement(G.A.HeaderCell,{width:3},N.M.t("Role")),f.createElement(G.A.HeaderCell,{width:1,textAlign:"right"},f.createElement(O.J,{community:n},f.createElement(g.Z,{rolesCanInvite:o,groupsEnabled:r,community:n,triggerButtonSize:"tiny"}))))),f.createElement(G.A.Body,null,t))};pe.propTypes={results:v().array.isRequired,community:v().object.isRequired,rolesCanInvite:v().object.isRequired,communityGroupsEnabled:v().bool.isRequired,config:v().object.isRequired};var be=n(71431),ye=n(1798);function fe(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function he(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?fe(Object(n),!0).forEach((function(t){(0,r.A)(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):fe(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}var ve=document.getElementById("community-members-search-root").dataset,Ae=JSON.parse(ve.communitiesRolesCanUpdate),Ce=JSON.parse(ve.communitiesAllRoles),Ee=JSON.parse(ve.community),Oe=JSON.parse(ve.permissions),ge=JSON.parse(ve.communityGroupsEnabled),Se=JSON.parse(ve.communitiesRolesCanInvite),ke="InvenioCommunities.ManagerSearch",Re=(0,i.parametrize)(be.f,{config:{rolesCanUpdate:Ae,visibility:a.S,permissions:Oe}}),Me=(0,i.parametrize)(pe,{community:Ee,communityGroupsEnabled:ge,rolesCanInvite:Se,config:{roles:Ce,visibility:a.S,permissions:Oe}}),je=(0,i.parametrize)(ye.K,{community:Ee}),we=(0,i.parametrize)(R,{community:Ee,communityGroupsEnabled:ge,rolesCanInvite:Se,permissions:Oe,roles:Ce,appName:ke}),xe=(0,i.parametrize)(D,{community:Ee,communityGroupsEnabled:ge,rolesCanInvite:Se}),qe=(0,r.A)((0,r.A)((0,r.A)((0,r.A)((0,r.A)((0,r.A)((0,r.A)((0,r.A)({},"".concat(ke,".EmptyResults.element"),xe),"".concat(ke,".ResultsList.item"),Re),"".concat(ke,".ResultsGrid.item"),u.L),"".concat(ke,".SearchApp.layout"),we),"".concat(ke,".SearchBar.element"),c.t),"".concat(ke,".SearchApp.results"),s.E),"".concat(ke,".ResultsList.container"),Me),"".concat(ke,".Sort.element"),l.ee),Ne=i.overrideStore.getAll();(0,o.U)(he(he({},qe),Ne),!0,"invenio-search-config",!0,je)}},e=>{e.O(0,[402,1057,7655,5373,6267,9777,5941,7501,4218,8010,5588,8102,742,6528,3532,1751,226,5580,4453,8803,6367],(()=>{return t=8299,e(e.s=t);var t}));e.O()}]);
//# sourceMappingURL=invenio-communities-members-manager.4c0e3f34acc12b0cb20b.js.map