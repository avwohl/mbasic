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
        // Wait for CodeMirror global to be available
        if (typeof CodeMirror === 'undefined') {
            console.error('CodeMirror not loaded!');
            return;
        }

        // Create CodeMirror 5 instance
        this.editor = CodeMirror(this.$el, {
            value: this.value || '',
            lineNumbers: true,
            readOnly: this.readonly || false,
            mode: 'text/plain'  // No syntax highlighting for now
        });

        // Handle changes
        this.editor.on('change', () => {
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

        addBreakpoint(lineNum) {
            if (!this.editor) return;

            // Find the actual editor line with this BASIC line number
            const doc = this.editor.getDoc();
            const lineCount = doc.lineCount();

            for (let i = 0; i < lineCount; i++) {
                const lineText = doc.getLine(i);
                const match = lineText.match(/^\s*(\d+)\s/);
                if (match && parseInt(match[1]) === lineNum) {
                    // Add line class for red background
                    this.editor.addLineClass(i, 'background', 'cm-breakpoint-line');
                    this.breakpointMarkers.push({line: i, basicLineNum: lineNum});
                    break;
                }
            }
        },

        removeBreakpoint(lineNum) {
            if (!this.editor) return;

            // Find and remove the breakpoint marker
            this.breakpointMarkers = this.breakpointMarkers.filter(bp => {
                if (bp.basicLineNum === lineNum) {
                    this.editor.removeLineClass(bp.line, 'background', 'cm-breakpoint-line');
                    return false;
                }
                return true;
            });
        },

        clearBreakpoints() {
            if (!this.editor) return;

            this.breakpointMarkers.forEach(bp => {
                this.editor.removeLineClass(bp.line, 'background', 'cm-breakpoint-line');
            });
            this.breakpointMarkers = [];
        },

        setCurrentStatement(lineNum) {
            if (!this.editor) return;

            // Clear previous current statement
            if (this.currentStatementMarker !== null) {
                this.editor.removeLineClass(this.currentStatementMarker, 'background', 'cm-current-statement');
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
                    this.editor.addLineClass(i, 'background', 'cm-current-statement');
                    this.currentStatementMarker = i;
                    // Scroll into view
                    this.editor.scrollIntoView({line: i, ch: 0}, 100);
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
