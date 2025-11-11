# Web UI Dialog Pattern

## Problem

Previously, dialogs were created inside menu click handlers:

```python
def _show_variables_window(self):
    with ui.dialog() as dialog, ui.card():
        # ... build dialog UI ...
        dialog.open()
```

This caused two major issues:
1. **Double-click bug**: Each click creates a NEW dialog instance
2. **Context issues**: Dialogs created inside `ui.menu()` context don't display properly

## Solution: Create Once, Reuse

Following NiceGUI best practices, create dialog classes that inherit from `ui.dialog`:

```python
class VariablesDialog(ui.dialog):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend

    def show(self):
        # Clear previous content
        self.clear()

        # Build dialog UI fresh each time
        with self, ui.card():
            ui.label('Current data here')
            ui.button('Close', on_click=self.close)

        # Open the dialog
        self.open()
```

Then instantiate ONCE in `build_ui()`:

```python
def build_ui(self):
    self.variables_dialog = VariablesDialog(self)
```

And menu handlers just call `.show()`:

```python
def _show_variables_window(self):
    self.variables_dialog.show()
```

## Benefits

1. **No double-click bugs**: Same dialog instance just re-opens
2. **No context issues**: Dialog created at proper scope
3. **Dynamic content**: `.clear()` and rebuild allows fresh data each time
4. **Much simpler code**: Menu handler is 1 line instead of 150 lines
5. **Follows NiceGUI best practices**: Official recommendation from maintainers

## Remaining Work

The following dialogs still need refactoring to this pattern:
- Open file dialog
- Save As dialog
- Merge file dialog
- Find/Replace dialog
- Smart Insert dialog
- Delete Lines dialog
- Renumber dialog
- Settings dialog
- About dialog

Each should follow the same pattern: Create class, instantiate in `build_ui()`, call `.show()` from handler.
