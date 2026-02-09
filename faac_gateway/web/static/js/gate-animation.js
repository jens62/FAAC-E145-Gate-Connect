/**
 * FAAC Gate Animation Web Component
 *
 * A reusable, self-contained gate animation component that can be embedded
 * in any web application (Flask, Home Assistant, OpenHAB, etc.)
 *
 * Usage:
 *   <gate-animation wing1="50" wing2="45"></gate-animation>
 *
 * Or programmatically:
 *   const gate = document.querySelector('gate-animation');
 *   gate.setWingPosition(1, 75);
 *   gate.setWingPosition(2, 75);
 */
class GateAnimation extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });

        // Gate geometry constants
        this.ROTATION_X = 125;
        this.FRAME_LEFT_CLOSED = 150;
        this.FRAME_RIGHT_CLOSED = 1725;
        this.FRAME_LEFT_DX = this.FRAME_LEFT_CLOSED - this.ROTATION_X;  // 25
        this.FRAME_RIGHT_DX = this.FRAME_RIGHT_CLOSED - this.ROTATION_X; // 1600
        this.FRAME_STROKE_CLOSED = 15;
        this.FRAME_STROKE_OPEN = 40;

        // Bar positions when closed (absolute x coordinates)
        this.barAbsolute = [271.15, 392.31, 513.46, 634.62, 755.77, 876.92,
                           998.08, 1119.23, 1240.38, 1361.54, 1482.69, 1603.85];
        this.barDX = this.barAbsolute.map(x => x - this.ROTATION_X);

        // Initialize with closed position
        this._wing1Position = 0;
        this._wing2Position = 0;

        this.render();
    }

    static get observedAttributes() {
        return ['wing1', 'wing2'];
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (oldValue === newValue) return;

        const position = parseFloat(newValue) || 0;
        if (name === 'wing1') {
            this._wing1Position = position;
            this.updateWingVisual(1, position);
        } else if (name === 'wing2') {
            this._wing2Position = position;
            this.updateWingVisual(2, position);
        }
    }

    render() {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    width: 100%;
                    height: 100%;
                }

                svg {
                    display: block;
                    width: 100%;
                    height: auto;
                }
            </style>

            <svg viewBox="-7.5 -7.5 3480 1330" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <symbol id="hinge" width="32" height="105">
                        <rect width="32" height="105" fill="#555" />
                        <line x1="0" y1="35" x2="32" y2="35" stroke="#888" stroke-width="1" />
                        <line x1="0" y1="70" x2="32" y2="70" stroke="#888" stroke-width="1" />
                    </symbol>

                    <symbol id="post">
                        <line x1="50" y1="0" x2="50" y2="1330" stroke="#555" stroke-width="100" />
                    </symbol>
                </defs>

                <!-- Left side -->
                <use href="#post" x="0" y="-7.5" />
                <use href="#hinge" x="105.25" y="10" />
                <use href="#hinge" x="105.25" y="1100" />

                <!-- Left wing -->
                <g id="wing1-group">
                    <line id="wing1-frame-top" y1="7.5" y2="7.5" stroke="#555" stroke-width="15" />
                    <line id="wing1-frame-bottom" y1="1207.5" y2="1207.5" stroke="#555" stroke-width="15" />
                    <line id="wing1-frame-left" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                    <line id="wing1-frame-right" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                    <line id="wing1-reinf-1" y1="242.5" y2="242.5" stroke="#555" stroke-width="15" />
                    <line id="wing1-reinf-2" y1="1092.5" y2="1092.5" stroke="#555" stroke-width="15" />
                    <line id="wing1-bar-1" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                    <line id="wing1-bar-2" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                    <line id="wing1-bar-3" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                    <line id="wing1-bar-4" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                    <line id="wing1-bar-5" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                    <line id="wing1-bar-6" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                    <line id="wing1-bar-7" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                    <line id="wing1-bar-8" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                    <line id="wing1-bar-9" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                    <line id="wing1-bar-10" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                    <line id="wing1-bar-11" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                    <line id="wing1-bar-12" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                </g>

                <!-- Right side (mirrored) -->
                <g transform="translate(3480, 0) scale(-1, 1)">
                    <use href="#post" x="0" y="-7.5" />
                    <use href="#hinge" x="105.25" y="10" />
                    <use href="#hinge" x="105.25" y="1100" />

                    <g id="wing2-group">
                        <line id="wing2-frame-top" y1="7.5" y2="7.5" stroke="#555" stroke-width="15" />
                        <line id="wing2-frame-bottom" y1="1207.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing2-frame-left" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing2-frame-right" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing2-reinf-1" y1="242.5" y2="242.5" stroke="#555" stroke-width="15" />
                        <line id="wing2-reinf-2" y1="1092.5" y2="1092.5" stroke="#555" stroke-width="15" />
                        <line id="wing2-bar-1" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing2-bar-2" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing2-bar-3" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing2-bar-4" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing2-bar-5" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing2-bar-6" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing2-bar-7" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing2-bar-8" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing2-bar-9" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing2-bar-10" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing2-bar-11" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing2-bar-12" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                    </g>
                </g>
            </svg>
        `;

        // Initialize gates at their current positions
        this.updateWingVisual(1, this._wing1Position);
        this.updateWingVisual(2, this._wing2Position);
    }

    /**
     * Update wing visual position
     * @param {number} wingId - Wing identifier (1 or 2)
     * @param {number} position - Position percentage (0-100)
     */
    updateWingVisual(wingId, position) {
        const angle = (position / 100) * (Math.PI / 2);
        const cosA = Math.cos(angle);
        const sinA = Math.sin(angle);

        const frameLeftX = this.ROTATION_X + this.FRAME_LEFT_DX * cosA;
        const frameRightX = this.ROTATION_X + this.FRAME_RIGHT_DX * cosA;
        const vertStroke = this.FRAME_STROKE_CLOSED * cosA + this.FRAME_STROKE_OPEN * sinA;
        const halfVS = vertStroke / 2;

        const root = this.shadowRoot;
        const prefix = `wing${wingId}`;

        const fl = root.getElementById(`${prefix}-frame-left`);
        if (fl) {
            fl.setAttribute('x1', frameLeftX);
            fl.setAttribute('x2', frameLeftX);
            fl.setAttribute('stroke-width', vertStroke);
        }

        const fr = root.getElementById(`${prefix}-frame-right`);
        if (fr) {
            fr.setAttribute('x1', frameRightX);
            fr.setAttribute('x2', frameRightX);
            fr.setAttribute('stroke-width', vertStroke);
        }

        const hLeft = frameLeftX - halfVS;
        const hRight = frameRightX + halfVS;

        const ft = root.getElementById(`${prefix}-frame-top`);
        if (ft) {
            ft.setAttribute('x1', hLeft);
            ft.setAttribute('x2', hRight);
        }

        const fb = root.getElementById(`${prefix}-frame-bottom`);
        if (fb) {
            fb.setAttribute('x1', hLeft);
            fb.setAttribute('x2', hRight);
        }

        const r1 = root.getElementById(`${prefix}-reinf-1`);
        if (r1) {
            r1.setAttribute('x1', frameLeftX);
            r1.setAttribute('x2', frameRightX);
        }

        const r2 = root.getElementById(`${prefix}-reinf-2`);
        if (r2) {
            r2.setAttribute('x1', frameLeftX);
            r2.setAttribute('x2', frameRightX);
        }

        for (let i = 0; i < 12; i++) {
            const barX = this.ROTATION_X + this.barDX[i] * cosA;
            const bar = root.getElementById(`${prefix}-bar-${i + 1}`);
            if (bar) {
                bar.setAttribute('x1', barX);
                bar.setAttribute('x2', barX);
            }
        }
    }

    /**
     * Public API: Set wing position programmatically
     * @param {number} wingId - Wing identifier (1 or 2)
     * @param {number} position - Position percentage (0-100)
     */
    setWingPosition(wingId, position) {
        const clampedPosition = Math.max(0, Math.min(100, position));

        if (wingId === 1) {
            this._wing1Position = clampedPosition;
            this.setAttribute('wing1', clampedPosition);
        } else if (wingId === 2) {
            this._wing2Position = clampedPosition;
            this.setAttribute('wing2', clampedPosition);
        }
    }

    /**
     * Public API: Get current wing position
     * @param {number} wingId - Wing identifier (1 or 2)
     * @returns {number} Current position (0-100)
     */
    getWingPosition(wingId) {
        return wingId === 1 ? this._wing1Position : this._wing2Position;
    }
}

// Register the custom element
customElements.define('gate-animation', GateAnimation);
