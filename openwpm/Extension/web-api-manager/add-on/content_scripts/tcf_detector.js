(function () {
    "use strict";

    const {browserLib} = window.WEB_API_MANAGER;

    document.addEventListener('DOMContentLoaded', detectTCF, false);
    
    function detectTCF() {

        
        
        const log_tcf = function() {
            const tcf_iframe    = document.querySelector('iframe[name="__tcfapiLocator"]');
            const tcf_function  = window.__tcfapi;

            if (tcf_iframe !== undefined && tcf_function !== undefined && typeof window.__tcfapi === "function") {
                // The TCF is detected, logging this information
                console.log('The TCF is detected');

                // TODO - trigger an event
                const doc = window.document;
                const blockEvent = new window.CustomEvent('__wam_tcf_detected', {});
                document.dispatchEvent.call(doc, blockEvent);
            }
        }

        const injectScript = function () {
            
            const doc = window.document;
            const script = doc.createElement("script");
            const rootElm = doc.head || doc.documentElement;
            console.log('I am gonna try to append the script to the ', rootElm);
            
            const scriptToInject = "(" + log_tcf.toString() + "())";
            
            script.appendChild(doc.createTextNode(scriptToInject));
            rootElm.appendChild(script);
        }

        window.document.addEventListener('__wam_tcf_detected', function (e) {
            const toBeSent = {
                ordinal: 0,
                scriptUrl: '',
                scriptLine: '0',
                scriptCol: '0',
                funcName: '',
                scriptLocEval: '',
                callStack: '',
                symbol: '',
                operation: 'tcf-detected',
                value: '',
                // // TODO
                timeStamp: Date.now(),
                // TODO
                args: []
            };
    
            browserLib.getRootObject().runtime.sendMessage([
                "interceptedFeatureAccess",
                {
                    namespace: 'javascript-instrumentation',
                    type: 'logTcfDetectionlogCall',
                    data: toBeSent
                }
            ]);
        }, false);

    }

}());