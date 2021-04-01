/**
 * Modified sockets library from OpenWPM default extension
 * 
 * Integrated to the Web API Manager by Marek Schauer
 * 
 * Year: 2021
 */
(function () {
    "use strict";

    let DataReceiver = {
        callbacks: new Map(),
        onDataReceived: (aSocketId, aData, aJSON) => {
            if (!DataReceiver.callbacks.has(aSocketId)) {
                return;
            }
            if (aJSON) {
                aData = JSON.parse(aData);
            }
            DataReceiver.callbacks.get(aSocketId)(aData);
        },
    };

    browser.sockets.onDataReceived.addListener(DataReceiver.onDataReceived);

    let ListeningSockets = new Map();

    class ListeningSocket {
        constructor(callback) {
            this.callback = callback
        }

        async startListening() {
            this.port = await browser.sockets.createServerSocket();
            DataReceiver.callbacks.set(this.port, this.callback);
            browser.sockets.startListening(this.port);
            console.log('Listening on port ' + this.port);
        }
    }

    class SendingSocket {
        constructor() {}

        async connect(host, port) {
            this.id = await browser.sockets.createSendingSocket();
            browser.sockets.connect(this.id, host, port);
            console.log(`Connected to ${host}:${port}`);
        }

        send(aData, aJSON = true) {
            try {
                browser.sockets.sendData(this.id, aData, !!aJSON);
                return true;
            } catch (err) {
                console.error(err, err.message);
                return false;
            }
        }

        close() {
            browser.sockets.close(this.id);
        }
    }

    window.WEB_API_MANAGER.socketsLib = {
        SendingSocket,
        ListeningSocket
    };
}());
  