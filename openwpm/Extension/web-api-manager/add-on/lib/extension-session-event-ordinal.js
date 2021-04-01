/**
 * Adapted from OpenWPM Extension by Marek Schauer
 * 
 * This enables us to keep information about the original order
 * in which events arrived to our event listeners.
 */
(function () {
    let eventOrdinal = 0;

    incrementedEventOrdinal = () => {
        return eventOrdinal++;
    };

    window.WEB_API_MANAGER.incrementedEventOrdinal = {
        incrementedEventOrdinal,
    }
}());
