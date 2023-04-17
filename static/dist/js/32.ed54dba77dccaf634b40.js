/*! For license information please see 32.ed54dba77dccaf634b40.js.LICENSE.txt */
(window.webpackJsonp=window.webpackJsonp||[]).push([[32],{1165:function(e,t,r){"use strict";r.r(t);var n=r(14),o=r.n(n),a=r(12),i=r.n(a),u=r(2),c=r.n(u),s=r(6),f=r.n(s),l=r(7),d=r.n(l),p=r(9),h=r.n(p),v=r(10),m=r.n(v),g=r(3),y=r.n(g),x=r(23),w=r.n(x),b=r(8),E=r.n(b),L=r(36),_=r.n(L),j=r(0),O=r.n(j),k=r(33),R=r.n(k),P=r(15),q=r(30),S=r(637),T=r(84),F=r(135),I=r(1),M=r.n(I),N=["size","isLoading","children"];function G(e){var t=function(){if("undefined"===typeof Reflect||!Reflect.construct)return!1;if(Reflect.construct.sham)return!1;if("function"===typeof Proxy)return!0;try{return Boolean.prototype.valueOf.call(Reflect.construct(Boolean,[],(function(){}))),!0}catch(e){return!1}}();return function(){var r,n=y()(e);if(t){var o=y()(this).constructor;r=Reflect.construct(n,arguments,o)}else r=n.apply(this,arguments);return m()(this,r)}}var D=function(e){for(var t=e.size,r=e.isLoading,n=e.children,o=(w()(e,N),function(){return O.a.createElement(q.a.Column,{width:3},O.a.createElement(S.a,null,O.a.createElement(S.a.Image,{square:!0})),O.a.createElement(S.a,null,O.a.createElement(S.a.Paragraph,null,O.a.createElement(S.a.Line,{length:"medium"}),O.a.createElement(S.a.Line,{length:"short"}))))}),a=[],i=0;i<t;i++)a.push(O.a.createElement(o,{key:i}));return r?O.a.createElement(q.a,{columns:"equal",stackable:!0},a):n};D.propTypes={size:M.a.number,isLoading:M.a.bool.isRequired,children:M.a.node.isRequired},D.defaultProps={size:5};var C=function(e){var t=e.message;return O.a.createElement(T.a,{icon:"info",header:t})};C.propTypes={message:M.a.string.isRequired};var z=function(e){h()(r,e);var t=G(r);function r(){return f()(this,r),t.apply(this,arguments)}return d()(r,[{key:"render",value:function(){var e=this.props,t=e.community,r=e.defaultLogo;return O.a.createElement(F.a,{fluid:!0,href:"/communities/".concat(t.slug)},O.a.createElement(P.Image,{wrapped:!0,centered:!0,ui:!1,src:t.links.logo,fallbackSrc:r,loadFallbackFirst:!0}),O.a.createElement(F.a.Content,null,O.a.createElement(F.a.Header,null,_()(t.metadata.title,{length:30})),t.metadata.description&&O.a.createElement(F.a.Description,null,O.a.createElement("div",{className:"truncate-lines-2",dangerouslySetInnerHTML:{__html:t.metadata.description}}))))}}]),r}(j.Component);z.propTypes={community:M.a.object.isRequired,defaultLogo:M.a.string.isRequired};var U=function(e){h()(r,e);var t=G(r);function r(e){var n;return f()(this,r),n=t.call(this,e),c()(i()(n),"fetchData",o()(E.a.mark((function e(){var t,r;return E.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return t=n.props.fetchDataUrl,n.setState({isLoading:!0}),n.cancellableFetch=Object(P.withCancel)(P.http.get(t)),e.prev=3,e.next=6,n.cancellableFetch.promise;case 6:r=e.sent,n.setState({data:r.data.hits,isLoading:!1}),e.next=12;break;case 10:e.prev=10,e.t0=e.catch(3);case 12:case"end":return e.stop()}}),e,null,[[3,10]])})))),n.state={isLoading:!1,data:{hits:[]}},n}return d()(r,[{key:"componentDidMount",value:function(){this.fetchData()}},{key:"componentWillUnmount",value:function(){this.cancellableFetch&&this.cancellableFetch.cancel()}},{key:"renderCards",value:function(){var e=this.state.data,t=this.props.defaultLogo;return e.hits.map((function(e){return O.a.createElement(z,{key:e.id,community:e,defaultLogo:t})}))}},{key:"render",value:function(){var e=this.state,t=e.isLoading,r=e.data,n=this.props.emptyMessage;return O.a.createElement(D,{isLoading:t},0===r.hits.length?O.a.createElement(C,{message:n}):O.a.createElement(F.a.Group,{doubling:!0,stackable:!0,itemsPerRow:5,className:"community-frontpage-cards"},this.renderCards()))}}]),r}(j.Component);U.propTypes={fetchDataUrl:M.a.string.isRequired,defaultLogo:M.a.string.isRequired,emptyMessage:M.a.string.isRequired};var B=document.getElementById("user-communities"),Y=document.getElementById("featured-communities");B&&R.a.render(O.a.createElement(U,{fetchDataUrl:"/api/user/communities?q=&sort=newest&page=1&size=5",emptyMessage:"You are not a member of any community.",defaultLogo:"/static/images/square-placeholder.png"}),B),R.a.render(O.a.createElement(U,{fetchDataUrl:"/api/communities?q=&sort=newest&page=1&size=5",emptyMessage:"There are no featured communities.",defaultLogo:"/static/images/square-placeholder.png"}),Y),t.default=U},14:function(e,t){function r(e,t,r,n,o,a,i){try{var u=e[a](i),c=u.value}catch(s){return void r(s)}u.done?t(c):Promise.resolve(c).then(n,o)}e.exports=function(e){return function(){var t=this,n=arguments;return new Promise((function(o,a){var i=e.apply(t,n);function u(e){r(i,o,a,u,c,"next",e)}function c(e){r(i,o,a,u,c,"throw",e)}u(void 0)}))}},e.exports.__esModule=!0,e.exports.default=e.exports},147:function(e,t,r){var n=r(148),o=r(297),a=r(298),i=a&&a.isRegExp,u=i?o(i):n;e.exports=u},148:function(e,t,r){var n=r(50),o=r(47);e.exports=function(e){return o(e)&&"[object RegExp]"==n(e)}},149:function(e,t,r){var n=r(150),o=r(38),a=r(151);e.exports=function(e){return o(e)?a(e):n(e)}},150:function(e,t,r){var n=r(311)("length");e.exports=n},151:function(e,t){var r="\\ud800-\\udfff",n="["+r+"]",o="[\\u0300-\\u036f\\ufe20-\\ufe2f\\u20d0-\\u20ff]",a="\\ud83c[\\udffb-\\udfff]",i="[^"+r+"]",u="(?:\\ud83c[\\udde6-\\uddff]){2}",c="[\\ud800-\\udbff][\\udc00-\\udfff]",s="(?:"+o+"|"+a+")"+"?",f="[\\ufe0e\\ufe0f]?",l=f+s+("(?:\\u200d(?:"+[i,u,c].join("|")+")"+f+s+")*"),d="(?:"+[i+o+"?",o,u,c,n].join("|")+")",p=RegExp(a+"(?="+a+")|"+d+l,"g");e.exports=function(e){for(var t=p.lastIndex=0;p.test(e);)++t;return t}},152:function(e,t,r){var n=r(312),o=1/0;e.exports=function(e){return e?(e=n(e))===o||e===-1/0?17976931348623157e292*(e<0?-1:1):e===e?e:0:0===e?e:0}},23:function(e,t,r){var n=r(87);e.exports=function(e,t){if(null==e)return{};var r,o,a=n(e,t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(o=0;o<i.length;o++)r=i[o],t.indexOf(r)>=0||Object.prototype.propertyIsEnumerable.call(e,r)&&(a[r]=e[r])}return a},e.exports.__esModule=!0,e.exports.default=e.exports},36:function(e,t,r){var n=r(310),o=r(66),a=r(38),i=r(43),u=r(147),c=r(149),s=r(67),f=r(72),l=r(45),d=/\w*$/;e.exports=function(e,t){var r=30,p="...";if(i(t)){var h="separator"in t?t.separator:h;r="length"in t?f(t.length):r,p="omission"in t?n(t.omission):p}var v=(e=l(e)).length;if(a(e)){var m=s(e);v=m.length}if(r>=v)return e;var g=r-c(p);if(g<1)return p;var y=m?o(m,0,g).join(""):e.slice(0,g);if(void 0===h)return y+p;if(m&&(g+=y.length-g),u(h)){if(e.slice(g).search(h)){var x,w=y;for(h.global||(h=RegExp(h.source,l(d.exec(h))+"g")),h.lastIndex=0;x=h.exec(w);)var b=x.index;y=y.slice(0,void 0===b?g:b)}}else if(e.indexOf(n(h),g)!=g){var E=y.lastIndexOf(h);E>-1&&(y=y.slice(0,E))}return y+p}},38:function(e,t){var r=RegExp("[\\u200d\\ud800-\\udfff\\u0300-\\u036f\\ufe20-\\ufe2f\\u20d0-\\u20ff\\ufe0e\\ufe0f]");e.exports=function(e){return r.test(e)}},66:function(e,t,r){var n=r(296);e.exports=function(e,t,r){var o=e.length;return r=void 0===r?o:r,!t&&r>=o?e:n(e,t,r)}},67:function(e,t,r){var n=r(94),o=r(38),a=r(95);e.exports=function(e){return o(e)?a(e):n(e)}},72:function(e,t,r){var n=r(152);e.exports=function(e){var t=n(e),r=t%1;return t===t?r?t-r:t:0}},8:function(e,t,r){var n=r(89)();e.exports=n;try{regeneratorRuntime=n}catch(o){"object"===typeof globalThis?globalThis.regeneratorRuntime=n:Function("r","regeneratorRuntime = r")(n)}},87:function(e,t){e.exports=function(e,t){if(null==e)return{};var r,n,o={},a=Object.keys(e);for(n=0;n<a.length;n++)r=a[n],t.indexOf(r)>=0||(o[r]=e[r]);return o},e.exports.__esModule=!0,e.exports.default=e.exports},89:function(e,t,r){var n=r(37).default;function o(){"use strict";e.exports=o=function(){return t},e.exports.__esModule=!0,e.exports.default=e.exports;var t={},r=Object.prototype,a=r.hasOwnProperty,i=Object.defineProperty||function(e,t,r){e[t]=r.value},u="function"==typeof Symbol?Symbol:{},c=u.iterator||"@@iterator",s=u.asyncIterator||"@@asyncIterator",f=u.toStringTag||"@@toStringTag";function l(e,t,r){return Object.defineProperty(e,t,{value:r,enumerable:!0,configurable:!0,writable:!0}),e[t]}try{l({},"")}catch(S){l=function(e,t,r){return e[t]=r}}function d(e,t,r,n){var o=t&&t.prototype instanceof v?t:v,a=Object.create(o.prototype),u=new R(n||[]);return i(a,"_invoke",{value:_(e,r,u)}),a}function p(e,t,r){try{return{type:"normal",arg:e.call(t,r)}}catch(S){return{type:"throw",arg:S}}}t.wrap=d;var h={};function v(){}function m(){}function g(){}var y={};l(y,c,(function(){return this}));var x=Object.getPrototypeOf,w=x&&x(x(P([])));w&&w!==r&&a.call(w,c)&&(y=w);var b=g.prototype=v.prototype=Object.create(y);function E(e){["next","throw","return"].forEach((function(t){l(e,t,(function(e){return this._invoke(t,e)}))}))}function L(e,t){function r(o,i,u,c){var s=p(e[o],e,i);if("throw"!==s.type){var f=s.arg,l=f.value;return l&&"object"==n(l)&&a.call(l,"__await")?t.resolve(l.__await).then((function(e){r("next",e,u,c)}),(function(e){r("throw",e,u,c)})):t.resolve(l).then((function(e){f.value=e,u(f)}),(function(e){return r("throw",e,u,c)}))}c(s.arg)}var o;i(this,"_invoke",{value:function(e,n){function a(){return new t((function(t,o){r(e,n,t,o)}))}return o=o?o.then(a,a):a()}})}function _(e,t,r){var n="suspendedStart";return function(o,a){if("executing"===n)throw new Error("Generator is already running");if("completed"===n){if("throw"===o)throw a;return q()}for(r.method=o,r.arg=a;;){var i=r.delegate;if(i){var u=j(i,r);if(u){if(u===h)continue;return u}}if("next"===r.method)r.sent=r._sent=r.arg;else if("throw"===r.method){if("suspendedStart"===n)throw n="completed",r.arg;r.dispatchException(r.arg)}else"return"===r.method&&r.abrupt("return",r.arg);n="executing";var c=p(e,t,r);if("normal"===c.type){if(n=r.done?"completed":"suspendedYield",c.arg===h)continue;return{value:c.arg,done:r.done}}"throw"===c.type&&(n="completed",r.method="throw",r.arg=c.arg)}}}function j(e,t){var r=t.method,n=e.iterator[r];if(void 0===n)return t.delegate=null,"throw"===r&&e.iterator.return&&(t.method="return",t.arg=void 0,j(e,t),"throw"===t.method)||"return"!==r&&(t.method="throw",t.arg=new TypeError("The iterator does not provide a '"+r+"' method")),h;var o=p(n,e.iterator,t.arg);if("throw"===o.type)return t.method="throw",t.arg=o.arg,t.delegate=null,h;var a=o.arg;return a?a.done?(t[e.resultName]=a.value,t.next=e.nextLoc,"return"!==t.method&&(t.method="next",t.arg=void 0),t.delegate=null,h):a:(t.method="throw",t.arg=new TypeError("iterator result is not an object"),t.delegate=null,h)}function O(e){var t={tryLoc:e[0]};1 in e&&(t.catchLoc=e[1]),2 in e&&(t.finallyLoc=e[2],t.afterLoc=e[3]),this.tryEntries.push(t)}function k(e){var t=e.completion||{};t.type="normal",delete t.arg,e.completion=t}function R(e){this.tryEntries=[{tryLoc:"root"}],e.forEach(O,this),this.reset(!0)}function P(e){if(e){var t=e[c];if(t)return t.call(e);if("function"==typeof e.next)return e;if(!isNaN(e.length)){var r=-1,n=function t(){for(;++r<e.length;)if(a.call(e,r))return t.value=e[r],t.done=!1,t;return t.value=void 0,t.done=!0,t};return n.next=n}}return{next:q}}function q(){return{value:void 0,done:!0}}return m.prototype=g,i(b,"constructor",{value:g,configurable:!0}),i(g,"constructor",{value:m,configurable:!0}),m.displayName=l(g,f,"GeneratorFunction"),t.isGeneratorFunction=function(e){var t="function"==typeof e&&e.constructor;return!!t&&(t===m||"GeneratorFunction"===(t.displayName||t.name))},t.mark=function(e){return Object.setPrototypeOf?Object.setPrototypeOf(e,g):(e.__proto__=g,l(e,f,"GeneratorFunction")),e.prototype=Object.create(b),e},t.awrap=function(e){return{__await:e}},E(L.prototype),l(L.prototype,s,(function(){return this})),t.AsyncIterator=L,t.async=function(e,r,n,o,a){void 0===a&&(a=Promise);var i=new L(d(e,r,n,o),a);return t.isGeneratorFunction(r)?i:i.next().then((function(e){return e.done?e.value:i.next()}))},E(b),l(b,f,"Generator"),l(b,c,(function(){return this})),l(b,"toString",(function(){return"[object Generator]"})),t.keys=function(e){var t=Object(e),r=[];for(var n in t)r.push(n);return r.reverse(),function e(){for(;r.length;){var n=r.pop();if(n in t)return e.value=n,e.done=!1,e}return e.done=!0,e}},t.values=P,R.prototype={constructor:R,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=void 0,this.done=!1,this.delegate=null,this.method="next",this.arg=void 0,this.tryEntries.forEach(k),!e)for(var t in this)"t"===t.charAt(0)&&a.call(this,t)&&!isNaN(+t.slice(1))&&(this[t]=void 0)},stop:function(){this.done=!0;var e=this.tryEntries[0].completion;if("throw"===e.type)throw e.arg;return this.rval},dispatchException:function(e){if(this.done)throw e;var t=this;function r(r,n){return i.type="throw",i.arg=e,t.next=r,n&&(t.method="next",t.arg=void 0),!!n}for(var n=this.tryEntries.length-1;n>=0;--n){var o=this.tryEntries[n],i=o.completion;if("root"===o.tryLoc)return r("end");if(o.tryLoc<=this.prev){var u=a.call(o,"catchLoc"),c=a.call(o,"finallyLoc");if(u&&c){if(this.prev<o.catchLoc)return r(o.catchLoc,!0);if(this.prev<o.finallyLoc)return r(o.finallyLoc)}else if(u){if(this.prev<o.catchLoc)return r(o.catchLoc,!0)}else{if(!c)throw new Error("try statement without catch or finally");if(this.prev<o.finallyLoc)return r(o.finallyLoc)}}}},abrupt:function(e,t){for(var r=this.tryEntries.length-1;r>=0;--r){var n=this.tryEntries[r];if(n.tryLoc<=this.prev&&a.call(n,"finallyLoc")&&this.prev<n.finallyLoc){var o=n;break}}o&&("break"===e||"continue"===e)&&o.tryLoc<=t&&t<=o.finallyLoc&&(o=null);var i=o?o.completion:{};return i.type=e,i.arg=t,o?(this.method="next",this.next=o.finallyLoc,h):this.complete(i)},complete:function(e,t){if("throw"===e.type)throw e.arg;return"break"===e.type||"continue"===e.type?this.next=e.arg:"return"===e.type?(this.rval=this.arg=e.arg,this.method="return",this.next="end"):"normal"===e.type&&t&&(this.next=t),h},finish:function(e){for(var t=this.tryEntries.length-1;t>=0;--t){var r=this.tryEntries[t];if(r.finallyLoc===e)return this.complete(r.completion,r.afterLoc),k(r),h}},catch:function(e){for(var t=this.tryEntries.length-1;t>=0;--t){var r=this.tryEntries[t];if(r.tryLoc===e){var n=r.completion;if("throw"===n.type){var o=n.arg;k(r)}return o}}throw new Error("illegal catch attempt")},delegateYield:function(e,t,r){return this.delegate={iterator:P(e),resultName:t,nextLoc:r},"next"===this.method&&(this.arg=void 0),h}},t}e.exports=o,e.exports.__esModule=!0,e.exports.default=e.exports},94:function(e,t){e.exports=function(e){return e.split("")}},95:function(e,t){var r="\\ud800-\\udfff",n="["+r+"]",o="[\\u0300-\\u036f\\ufe20-\\ufe2f\\u20d0-\\u20ff]",a="\\ud83c[\\udffb-\\udfff]",i="[^"+r+"]",u="(?:\\ud83c[\\udde6-\\uddff]){2}",c="[\\ud800-\\udbff][\\udc00-\\udfff]",s="(?:"+o+"|"+a+")"+"?",f="[\\ufe0e\\ufe0f]?",l=f+s+("(?:\\u200d(?:"+[i,u,c].join("|")+")"+f+s+")*"),d="(?:"+[i+o+"?",o,u,c,n].join("|")+")",p=RegExp(a+"(?="+a+")|"+d+l,"g");e.exports=function(e){return e.match(p)||[]}}},[[1165,0,1]]]);
//# sourceMappingURL=32.ed54dba77dccaf634b40.js.map