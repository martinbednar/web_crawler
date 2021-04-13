(function () {
    "use strict";

    const {browserLib} = window.WEB_API_MANAGER;


    document.addEventListener('DOMContentLoaded', detectTCF, false);
    
    function detectTCF() {

        
        
        const log_tcf = function() {
            setTimeout(function () {
                const tcf_iframe    = document.querySelector('iframe[name="__tcfapiLocator"]');
                const tcf_function  = window.__tcfapi;
    
                if (tcf_iframe !== undefined && tcf_function !== undefined && typeof window.__tcfapi === "function") {
                    // The TCF is detected, logging this information
                    console.log('The TCF is detected');

                    // TODO - trigger an event
                    const doc = window.document;
                    const blockEvent = new window.CustomEvent('__wam_tcf_detected', {});
                    document.dispatchEvent.call(doc, blockEvent);
                } else {
                    // console.log('The TCF was not detected', 'tcf_iframe:', tcf_iframe, 'tcf_function:', tcf_function);
                }
            }, 5000);
        }

        /**
         * injectScript - Inject internal script to available access to the `window`
         *
         * @param  {type} file_path Local path of the internal script.
         * @param  {type} tag The tag as string, where the script will be append (default: 'body').
         * @see    {@link http://stackoverflow.com/questions/20499994/access-window-variable-from-content-script}
         */
        const injectScript = function () {
            
            const doc = window.document;
            const script = doc.createElement("script");
            const rootElm = doc.head || doc.documentElement;
            console.log('I am gonna try to append the script to the ', rootElm);
            
            const scriptToInject = "(" + log_tcf.toString() + "())";
            
            
            script.appendChild(doc.createTextNode(scriptToInject));
            rootElm.appendChild(script);
            
            
            // var nodes = document.getElementsByTagName(tag);
            
            // for (let i = 0; i < nodes.length; i++) {
            //     const node = nodes[i];
            //     var script = document.createElement('script');
            //     script.setAttribute('type', 'text/javascript');
            //     script.setAttribute('src', file_path);
            //     console.log('I added script to this node:', node);
            // }
        }

        // TODO - create an event listener that handles the detected TCF
        // Listen for the event.
        // elem.addEventListener('__wam_tcf_detected', function (e) { /* ... */ }, false);
        window.document.addEventListener('__wam_tcf_detected', function (e) {
            console.log('AAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'I have detected the TCF usage', 'AAAAAAAAAAAAAAAAAAAAAAAAAAAA');

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


        console.log('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!>>>',);
        console.log(injectScript());
        console.log('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^');









    }

}());