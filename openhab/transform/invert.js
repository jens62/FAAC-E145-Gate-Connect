/**
 * Invert position values for FAAC gate
 *
 * Hardware: 0=CLOSED, 100=OPEN
 * OpenHAB: 0=OPEN, 100=CLOSED
 *
 * This transformation inverts the values:
 * - Incoming (from gate): 0 → 100, 100 → 0
 * - Outgoing (to gate): 0 → 100, 100 → 0
 */

(function(input) {
    var value = parseInt(input);

    // Validate input
    if (isNaN(value)) {
        return input; // Return unchanged if not a number
    }

    // Invert: 100 - value
    var inverted = 100 - value;

    return inverted.toString();
})(input)
