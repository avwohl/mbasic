#!/usr/bin/env python3
"""
Basic NiceGUI interaction tests.

These tests demonstrate and verify that the NiceGUI testing framework works.
"""

import pytest
from nicegui import ui
from nicegui.testing import User


@pytest.mark.asyncio
async def test_button_click(user: User):
    """Test basic button click interaction."""
    counter = {'value': 0}

    def increment():
        counter['value'] += 1

    @ui.page('/')
    def page():
        ui.button('Click me', on_click=increment).mark('test_btn')
        ui.label().mark('counter').bind_text_from(counter, 'value')

    await user.open('/')

    # Initial state
    await user.should_see('0', marker='counter')

    # Click once
    user.find(marker='test_btn').click()
    await user.should_see('1', marker='counter')

    # Click again
    user.find(marker='test_btn').click()
    await user.should_see('2', marker='counter')


@pytest.mark.asyncio
async def test_input_text(user: User):
    """Test text input."""
    data = {'name': ''}

    @ui.page('/')
    def page():
        ui.input('Enter name:').mark('name_input').bind_value(data, 'name')
        ui.label().mark('greeting').bind_text_from(data, 'name',
                                                   backward=lambda n: f'Hello {n}!' if n else '')

    await user.open('/')

    # Type name
    user.find(marker='name_input').type('Alice')

    # Should see greeting
    await user.should_see('Hello Alice!', marker='greeting')


@pytest.mark.asyncio
async def test_visibility_toggle(user: User):
    """Test showing/hiding elements."""
    state = {'visible': True}

    def toggle():
        state['visible'] = not state['visible']

    @ui.page('/')
    def page():
        ui.button('Toggle', on_click=toggle).mark('toggle_btn')
        ui.label('Visible content').mark('content').bind_visibility_from(state, 'visible')

    await user.open('/')

    # Initially visible
    await user.should_see('Visible content', marker='content')

    # Toggle off
    user.find(marker='toggle_btn').click()
    await user.should_not_see('Visible content')

    # Toggle on
    user.find(marker='toggle_btn').click()
    await user.should_see('Visible content', marker='content')


@pytest.mark.asyncio
async def test_multiple_elements(user: User):
    """Test finding and interacting with multiple elements."""
    counters = [
        {'value': 0, 'label': 'Counter A'},
        {'value': 0, 'label': 'Counter B'},
        {'value': 0, 'label': 'Counter C'},
    ]

    @ui.page('/')
    def page():
        for i, counter in enumerate(counters):
            def make_increment(c):
                def increment():
                    c['value'] += 1
                return increment

            ui.button(counter['label'], on_click=make_increment(counter)).mark(f'btn_{i}')
            ui.label().mark(f'count_{i}').bind_text_from(counter, 'value')

    await user.open('/')

    # Click different buttons
    user.find(marker='btn_0').click()
    await user.should_see('1', marker='count_0')
    await user.should_see('0', marker='count_1')

    user.find(marker='btn_1').click()
    user.find(marker='btn_1').click()
    await user.should_see('1', marker='count_0')
    await user.should_see('2', marker='count_1')


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
