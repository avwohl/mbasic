/**
 * CodeMirror 5 Editor Component for NiceGUI
 *
 * Uses CodeMirror 5 (legacy) which doesn't require ES6 modules
 *
 * Provides:
 * - Find highlighting (yellow background via CSS class)
 * - Breakpoint markers (red line background)
 * - Current statement highlighting (green/blue background)
 * - Line numbers
 */

export default {
    template: '<div></div>',

    props: {
        value: String,
        readonly: Boolean
    },

    mounted() {
        // Inject CSS for breakpoint markers and find highlighting
        if (!document.getElementById('codemirror5-custom-styles')) {
            const style = document.createElement('style');
            style.id = 'codemirror5-custom-styles';
            style.textContent = `
                /* Find highlight - yellow background */
                .cm-find-highlight {
                    background-color: yellow;
                    color: black;
                }

                /* Breakpoint marker - light red background */
                .cm-breakpoint-marker {
                    background-color: #ffcccc;
                    border-bottom: 2px solid #cc0000;
                }

                /* Current statement during step debugging - light green background */
                .cm-current-statement {
                    background-color: #ccffcc;
                    border-bottom: 2px solid #00aa00;
                }

                /* Ensure CodeMirror fills its container */
                .CodeMirror {
                    height: 100%;
                    font-family: monospace;
                    font-size: 14px;
                }
            `;
            document.head.appendChild(style);
        }

        // Wait for CodeMirror global to be available
        if (typeof CodeMirror === 'undefined') {
            console.error('CodeMirror not loaded!');
            return;
        }

        // Create CodeMirror 5 instance
        this.editor = CodeMirror(this.$el, {
            value: this.value || '',
            lineNumbers: false,  // No line number gutter - BASIC programs have their own line numbers
            readOnly: this.readonly || false,
            mode: 'text/plain'  // No syntax highlighting for now
        });

        // Flag to skip change events during programmatic updates
        this.skipNextChange = false;

        // Handle changes
        this.editor.on('change', () => {
            // Skip if this is a programmatic update
            if (this.skipNextChange) {
                return;
            }
            const newValue = this.editor.getValue();
            this.$emit('change', newValue);
        });

        // Store markers for later cleanup
        this.findMarkers = [];
        this.breakpointMarkers = [];
        this.currentStatementMarker = null;
    },

    beforeUnmount() {
        if (this.editor) {
            this.editor.toTextArea();
        }
    },

    methods: {
        setValue(text) {
            if (this.editor) {
                this.editor.setValue(text);
            }
        },

        getValue() {
            return this.editor ? this.editor.getValue() : '';
        },

        addFindHighlight(line, startCol, endCol) {
            if (!this.editor) return;

            const marker = this.editor.markText(
                {line: line, ch: startCol},
                {line: line, ch: endCol},
                {className: 'cm-find-highlight'}
            );
            this.findMarkers.push(marker);
        },

        clearFindHighlights() {
            this.findMarkers.forEach(marker => marker.clear());
            this.findMarkers = [];
        },

        addBreakpoint(lineNum, charStart = null, charEnd = null) {
            if (!this.editor) return;

            // Find the actual editor line with this BASIC line number
            const doc = this.editor.getDoc();
            const lineCount = doc.lineCount();

            for (let i = 0; i < lineCount; i++) {
                const lineText = doc.getLine(i);
                const match = lineText.match(/^\s*(\d+)\s/);
                if (match && parseInt(match[1]) === lineNum) {
                    // Create text marker for specific statement or whole line
                    let marker;
                    if (charStart !== null && charEnd !== null && charStart >= 0 && charEnd > charStart) {
                        // Adjust charStart to include preceding space or colon
                        let adjustedStart = charStart;
                        if (charStart > 0 && lineText[charStart - 1] === ' ') {
                            adjustedStart = charStart - 1;  // Include space before statement
                        } else if (charStart > 0 && lineText[charStart - 1] === ':') {
                            adjustedStart = charStart - 1;  // Include colon before statement
                        }
                        // Highlight specific statement
                        marker = this.editor.markText(
                            {line: i, ch: adjustedStart},
                            {line: i, ch: charEnd},
                            {className: 'cm-breakpoint-marker'}
                        );
                    } else {
                        // Highlight entire line
                        marker = this.editor.markText(
                            {line: i, ch: 0},
                            {line: i, ch: lineText.length},
                            {className: 'cm-breakpoint-marker'}
                        );
                    }
                    this.breakpointMarkers.push({marker: marker, basicLineNum: lineNum});
                    break;
                }
            }
        },

        removeBreakpoint(lineNum) {
            if (!this.editor) return;

            // Find and remove the breakpoint marker
            this.breakpointMarkers = this.breakpointMarkers.filter(bp => {
                if (bp.basicLineNum === lineNum) {
                    bp.marker.clear();
                    return false;
                }
                return true;
            });
        },

        clearBreakpoints() {
            if (!this.editor) return;

            this.breakpointMarkers.forEach(bp => {
                bp.marker.clear();
            });
            this.breakpointMarkers = [];
        },

        setCurrentStatement(lineNum, charStart = null, charEnd = null) {
            if (!this.editor) return;

            // Clear previous current statement marker
            if (this.currentStatementMarker !== null) {
                this.currentStatementMarker.clear();
                this.currentStatementMarker = null;
            }

            if (lineNum === null) return;

            // Find the actual editor line with this BASIC line number
            const doc = this.editor.getDoc();
            const lineCount = doc.lineCount();

            for (let i = 0; i < lineCount; i++) {
                const lineText = doc.getLine(i);
                const match = lineText.match(/^\s*(\d+)\s/);
                if (match && parseInt(match[1]) === lineNum) {
                    // If char positions provided, highlight specific statement
                    // Otherwise highlight entire line
                    if (charStart !== null && charEnd !== null && charStart >= 0 && charEnd > charStart) {
                        // Highlight specific statement range
                        this.currentStatementMarker = this.editor.markText(
                            {line: i, ch: charStart},
                            {line: i, ch: charEnd},
                            {className: 'cm-current-statement'}
                        );
                    } else {
                        // Highlight entire line (for line stepping or no char info)
                        this.currentStatementMarker = this.editor.markText(
                            {line: i, ch: 0},
                            {line: i, ch: lineText.length},
                            {className: 'cm-current-statement'}
                        );
                    }
                    // Scroll into view
                    this.editor.scrollIntoView({line: i, ch: charStart || 0}, 100);
                    break;
                }
            }
        },

        scrollToLine(line) {
            if (this.editor) {
                this.editor.scrollIntoView({line: line, ch: 0}, 100);
            }
        },

        getCursorPosition() {
            if (!this.editor) return {line: 0, column: 0};

            const cursor = this.editor.getCursor();
            return {
                line: cursor.line,
                column: cursor.ch
            };
        },

        setCursor(line, column) {
            if (this.editor) {
                this.editor.setCursor({line: line, ch: column});
                this.editor.focus();
            }
        },

        setValueAndCursor(text, line, column) {
            if (this.editor) {
                // Temporarily disable change event to prevent recursive updates
                this.skipNextChange = true;
                this.editor.setValue(text);
                this.editor.setCursor({line: line, ch: column});
                this.editor.focus();
                // Re-enable immediately after setValue completes
                // Using nextTick to ensure setValue is done but user typing works immediately
                this.$nextTick(() => {
                    this.skipNextChange = false;
                });
            }
        },

        setReadonly(readonly) {
            if (this.editor) {
                this.editor.setOption('readOnly', readonly);
            }
        }
    },

    watch: {
        value(newValue) {
            if (this.editor && newValue !== this.editor.getValue()) {
                this.setValue(newValue);
            }
        },
        readonly(newValue) {
            if (this.editor) {
                this.setReadonly(newValue);
            }
        }
    }
};
