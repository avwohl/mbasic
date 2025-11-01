/**
 * CodeMirror 6 Editor Component for NiceGUI
 *
 * Provides a rich code editor with:
 * - Find highlighting (yellow background)
 * - Breakpoint markers (red gutter markers)
 * - Current statement highlighting (green/blue background)
 * - Line numbers
 */

import { EditorView, keymap, lineNumbers, highlightActiveLine } from "@codemirror/view";
import { EditorState, StateEffect, StateField } from "@codemirror/state";
import { defaultKeymap, history, historyKeymap } from "@codemirror/commands";
import { Decoration, WidgetType } from "@codemirror/view";

export default {
    template: '<div></div>',

    props: {
        value: String,
        readonly: Boolean
    },

    mounted() {
        // Extension for find highlights
        const findHighlightEffect = StateEffect.define();
        const findHighlightField = StateField.define({
            create() { return Decoration.none; },
            update(decorations, tr) {
                decorations = decorations.map(tr.changes);
                for (let effect of tr.effects) {
                    if (effect.is(findHighlightEffect)) {
                        decorations = effect.value;
                    }
                }
                return decorations;
            },
            provide: f => EditorView.decorations.from(f)
        });

        // Extension for breakpoint markers
        const breakpointEffect = StateEffect.define();
        const breakpointField = StateField.define({
            create() { return Decoration.none; },
            update(decorations, tr) {
                decorations = decorations.map(tr.changes);
                for (let effect of tr.effects) {
                    if (effect.is(breakpointEffect)) {
                        decorations = effect.value;
                    }
                }
                return decorations;
            },
            provide: f => EditorView.decorations.from(f)
        });

        // Extension for current statement highlight
        const currentStatementEffect = StateEffect.define();
        const currentStatementField = StateField.define({
            create() { return Decoration.none; },
            update(decorations, tr) {
                decorations = decorations.map(tr.changes);
                for (let effect of tr.effects) {
                    if (effect.is(currentStatementEffect)) {
                        decorations = effect.value;
                    }
                }
                return decorations;
            },
            provide: f => EditorView.decorations.from(f)
        });

        // Create editor
        this.view = new EditorView({
            state: EditorState.create({
                doc: this.value || '',
                extensions: [
                    lineNumbers(),
                    history(),
                    highlightActiveLine(),
                    keymap.of([...defaultKeymap, ...historyKeymap]),
                    findHighlightField,
                    breakpointField,
                    currentStatementField,
                    EditorView.updateListener.of((update) => {
                        if (update.docChanged) {
                            this.value = update.state.doc.toString();
                            this.$emit('change', this.value);
                        }
                    }),
                    EditorState.readOnly.of(this.readonly || false)
                ]
            }),
            parent: this.$el
        });

        // Store effects for later use
        this.findHighlightEffect = findHighlightEffect;
        this.breakpointEffect = breakpointEffect;
        this.currentStatementEffect = currentStatementEffect;

        // Store current decorations
        this.findHighlights = [];
        this.breakpoints = new Set();
        this.currentStatement = null;
    },

    beforeUnmount() {
        this.view.destroy();
    },

    methods: {
        setValue(text) {
            this.view.dispatch({
                changes: { from: 0, to: this.view.state.doc.length, insert: text }
            });
            this.value = text;
        },

        getValue() {
            return this.view.state.doc.toString();
        },

        addFindHighlight(line, startCol, endCol) {
            const doc = this.view.state.doc;
            const lineObj = doc.line(line + 1);  // CodeMirror lines are 1-based
            const from = lineObj.from + startCol;
            const to = lineObj.from + endCol;

            this.findHighlights.push({ line, startCol, endCol });

            const decorations = this.findHighlights.map(h => {
                const lineObj = doc.line(h.line + 1);
                const from = lineObj.from + h.startCol;
                const to = lineObj.from + h.endCol;
                return Decoration.mark({ class: 'cm-find-highlight' }).range(from, to);
            });

            this.view.dispatch({
                effects: this.findHighlightEffect.of(Decoration.set(decorations))
            });
        },

        clearFindHighlights() {
            this.findHighlights = [];
            this.view.dispatch({
                effects: this.findHighlightEffect.of(Decoration.none)
            });
        },

        addBreakpoint(lineNum) {
            this.breakpoints.add(lineNum);
            this.updateBreakpoints();
        },

        removeBreakpoint(lineNum) {
            this.breakpoints.delete(lineNum);
            this.updateBreakpoints();
        },

        clearBreakpoints() {
            this.breakpoints.clear();
            this.updateBreakpoints();
        },

        updateBreakpoints() {
            const doc = this.view.state.doc;
            const decorations = [];

            // Find lines with BASIC line numbers matching breakpoints
            for (let i = 1; i <= doc.lines; i++) {
                const lineText = doc.line(i).text;
                const match = lineText.match(/^\s*(\d+)\s/);
                if (match) {
                    const basicLineNum = parseInt(match[1]);
                    if (this.breakpoints.has(basicLineNum)) {
                        // Add line decoration (red background)
                        decorations.push(
                            Decoration.line({ class: 'cm-breakpoint-line' })
                                .range(doc.line(i).from)
                        );
                    }
                }
            }

            this.view.dispatch({
                effects: this.breakpointEffect.of(Decoration.set(decorations))
            });
        },

        setCurrentStatement(lineNum) {
            this.currentStatement = lineNum;

            if (lineNum === null) {
                this.view.dispatch({
                    effects: this.currentStatementEffect.of(Decoration.none)
                });
                return;
            }

            const doc = this.view.state.doc;
            const decorations = [];

            // Find line with matching BASIC line number
            for (let i = 1; i <= doc.lines; i++) {
                const lineText = doc.line(i).text;
                const match = lineText.match(/^\s*(\d+)\s/);
                if (match && parseInt(match[1]) === lineNum) {
                    decorations.push(
                        Decoration.line({ class: 'cm-current-statement' })
                            .range(doc.line(i).from)
                    );
                    break;
                }
            }

            this.view.dispatch({
                effects: this.currentStatementEffect.of(Decoration.set(decorations))
            });
        },

        scrollToLine(line) {
            const doc = this.view.state.doc;
            const lineObj = doc.line(line + 1);  // CodeMirror lines are 1-based
            this.view.dispatch({
                effects: EditorView.scrollIntoView(lineObj.from, { y: 'center' })
            });
        },

        getCursorPosition() {
            const pos = this.view.state.selection.main.head;
            const line = this.view.state.doc.lineAt(pos);
            return {
                line: line.number - 1,  // Convert to 0-based
                column: pos - line.from
            };
        },

        setReadonly(readonly) {
            this.view.dispatch({
                effects: StateEffect.reconfigure.of([
                    EditorState.readOnly.of(readonly)
                ])
            });
        }
    },

    watch: {
        value(newValue) {
            if (this.view && newValue !== this.view.state.doc.toString()) {
                this.setValue(newValue);
            }
        },
        readonly(newValue) {
            if (this.view) {
                this.setReadonly(newValue);
            }
        }
    }
};
