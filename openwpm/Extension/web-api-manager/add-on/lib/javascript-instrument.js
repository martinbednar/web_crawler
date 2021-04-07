(function () {
    "use strict";

    const {browserLib, incrementedEventOrdinal, extensionSessionUuid} = window.WEB_API_MANAGER;
    const {boolToInt, escapeString, escapeUrl} = window.WEB_API_MANAGER.stringUtils;
    // console.log('', incrementedEventOrdinal());

    
    /**
     * We don't need this
     * import MessageSender = browser.runtime.MessageSender;
     */
    // import {incrementedEventOrdinal} from "../lib/extension-session-event-ordinal";
    // import {extensionSessionUuid} from "../lib/extension-session-uuid";
    // import {boolToInt, escapeString, escapeUrl} from "../lib/string-utils";
    // import {JavascriptOperation} from "../schema";

    class JavascriptInstrument {
        /**
         * Converts received call and values data from the JS Instrumentation
         * into the format that the schema expects.
         * @param data
         * @param sender
         */
        static processCallsAndValues(data, sender) {
            const update = {};
            update.extension_session_uuid = extensionSessionUuid;
            update.event_ordinal = incrementedEventOrdinal.incrementedEventOrdinal();
            update.page_scoped_event_ordinal = data.ordinal;
            update.window_id = sender.tab.windowId;
            update.tab_id = sender.tab.id;
            update.frame_id = sender.frameId;
            update.script_url = escapeUrl(data.scriptUrl);
            update.script_line = escapeString(data.scriptLine);
            update.script_col = escapeString(data.scriptCol);
            update.func_name = escapeString(data.funcName);
            update.script_loc_eval = escapeString(data.scriptLocEval);
            update.call_stack = escapeString(data.callStack);
            update.symbol = escapeString(data.symbol);
            update.operation = escapeString(data.operation);
            update.value = escapeString(data.value);
            update.time_stamp = data.timeStamp;
            update.incognito = boolToInt(sender.tab.incognito);

            // document_url is the current frame's document href
            // top_level_url is the top-level frame's document href
            update.document_url = escapeUrl(sender.url);
            update.top_level_url = escapeUrl(sender.tab.url);

            if (data.operation === "call" && data.args.length > 0) {
                update.arguments = escapeString(JSON.stringify(data.args));
            }

            // console.log('If I was in OpenWPM, I would send this to the send method on loggingdb.js:', update);

            return update;
        }
        

        constructor(dataReceiver) {
            /*private, readonly*/
            this.dataReceiver = dataReceiver;

            // MS: we will move this to the constructor
            /*private*/
            this.onMessageListener = null;
            /*private, boolean*/
            this.configured = false;
            /*private, JavascriptOperation[]*/
            this.pendingRecords = [];
            /*private*/
            this.crawlID = null;
            // console.log('JavaScript Instrumentation class has been instantiated');
        }

        /**
         * Start listening for messages from page/content/background scripts injected to instrument JavaScript APIs
         */
        listen() {
            this.onMessageListener = (message, sender) => {
                const [label, data] = message;
                // console.log("I am receiving some message:", message);
                if (
                    data.namespace &&
                    data.namespace === "javascript-instrumentation"
                ) {
                    this.handleJsInstrumentationMessage(data, sender);
                }
            };
            
            // TODO - const rootObject = browserLib.getRootObject();
            browser.runtime.onMessage.addListener(this.onMessageListener);
        }

        /**
         * Either sends the log data to the dataReceiver or store it in memory
         * as a pending record if the JS instrumentation is not yet configured
         * @param message
         * @param sender
         */
        handleJsInstrumentationMessage(message, sender) {
            switch (message.type) {
            case "logCall":
            case "logValue":
                // console.log('I am here, handling the JsInstrumentationMessage, mesage=', message);
                const update = JavascriptInstrument.processCallsAndValues(
                    message.data,
                    sender,
                );
                if (this.configured) {
                    update.browser_id = this.crawlID;
                    this.dataReceiver.saveRecord("javascript", update);
                } else {
                    this.pendingRecords.push(update);
                }
                break;
            }
        }

        /**
         * Starts listening if haven't done so already, sets the crawl ID,
         * marks the JS instrumentation as configured and sends any pending
         * records that have been received up until this point.
         * @param crawlID
         */
        run(crawlID) {
            if (!this.onMessageListener) {
                this.listen();
            }
            this.crawlID = crawlID;
            this.configured = true;
            this.pendingRecords.map(update => {
                update.browser_id = this.crawlID;
                this.dataReceiver.saveRecord("javascript", update);
            });
        }

        // public async registerContentScript(
        //     testing: boolean,
        //     jsInstrumentationSettingsString: string,
        // ) {
        //     const contentScriptConfig = {
        //     testing,
        //     jsInstrumentationSettingsString,
        //     };
        //     if (contentScriptConfig) {
        //     // TODO: Avoid using window to pass the content script config
        //     await browser.contentScripts.register({
        //         js: [
        //         {
        //             code: `window.openWpmContentScriptConfig = ${JSON.stringify(
        //             contentScriptConfig,
        //             )};`,
        //         },
        //         ],
        //         matches: ["<all_urls>"],
        //         allFrames: true,
        //         runAt: "document_start",
        //         matchAboutBlank: true,
        //     });
        //     }
        //     return browser.contentScripts.register({
        //     js: [{ file: "/content.js" }],
        //     matches: ["<all_urls>"],
        //     allFrames: true,
        //     runAt: "document_start",
        //     matchAboutBlank: true,
        //     });
        // }

        cleanup() {
            this.pendingRecords = [];
            if (this.onMessageListener) {
                // TODO - const rootObject = browserLib.getRootObject();
                browser.runtime.onMessage.removeListener(this.onMessageListener);
            }
        }
    }

    window.WEB_API_MANAGER.jsInstrumentLib = {
        JavascriptInstrument,
    }
}());