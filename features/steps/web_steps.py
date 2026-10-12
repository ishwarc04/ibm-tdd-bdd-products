"""Browser step definitions used by the product feature."""
from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

def field(context, name):
    return context.driver.find_element(By.ID, "product_" + name.lower())

@when('I visit the "Home Page"')
def step_visit_home(context):
    context.driver.get(context.base_url)

@when('I set the "{name}" to "{value}"')
@when('I change "{name}" to "{value}"')
def step_set_field(context, name, value):
    element = field(context, name)
    element.clear()
    element.send_keys(value)

@when('I select "{value}" in the "{name}" dropdown')
def step_select(context, value, name):
    Select(field(context, name)).select_by_visible_text(value)

@when('I press the "{button}" button')
@when('I click the "{button}" button')
def step_press_button(context, button):
    """Task 7a: resolve button ID and click the actual browser element."""
    button_id = button.lower() + "-btn"
    WebDriverWait(context.driver, context.wait_seconds).until(
        EC.element_to_be_clickable((By.ID, button_id))
    ).click()
    if button.lower() != "clear":
        WebDriverWait(context.driver, context.wait_seconds).until(
            lambda driver: driver.find_element(By.ID, "flash_message").text != ""
        )

@when('I copy the "{name}" field')
def step_copy(context, name):
    context.copied_value = field(context, name).get_attribute("value")
    assert context.copied_value, f"{name} is empty"

@when('I paste the "{name}" field')
def step_paste(context, name):
    context.driver.execute_script("arguments[0].value = arguments[1]", field(context, name), context.copied_value)

@then('I should see "{text}" in the results')
def step_results_contain(context, text):
    """Task 7b: wait for expected result text."""
    WebDriverWait(context.driver, context.wait_seconds).until(
        EC.text_to_be_present_in_element((By.ID, "search_results"), text)
    )

@then('I should not see "{text}" in the results')
def step_results_exclude(context, text):
    """Task 7c: verify text is absent from the completed result table."""
    element = context.driver.find_element(By.ID, "search_results")
    assert text not in element.text, f"Unexpected result: {text}"

@then('I should see the message "{message}"')
def step_message(context, message):
    """Task 7d: wait for the expected feedback message."""
    WebDriverWait(context.driver, context.wait_seconds).until(
        EC.text_to_be_present_in_element((By.ID, "flash_message"), message)
    )

@then('I should see "{value}" in the "{name}" field')
def step_field_value(context, value, name):
    WebDriverWait(context.driver, context.wait_seconds).until(
        lambda driver: field(context, name).get_attribute("value") == value
    )

@then('I should see "{value}" in the "{name}" dropdown')
def step_dropdown_value(context, value, name):
    assert Select(field(context, name)).first_selected_option.text == value
