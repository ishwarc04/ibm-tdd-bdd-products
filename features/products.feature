Feature: Product Management
  As a product manager
  I need to maintain and search the product catalog
  So that customers can find current product information

  Background:
    Given the following products
      | name    | description     | price | available | category   |
      | Hat     | A red fedora    | 59.95 | True      | CLOTHS     |
      | Shoes   | Running shoes   | 89.95 | False     | CLOTHS     |
      | Big Mac | A tasty burger  | 5.99  | True      | FOOD       |
      | Sheets  | Cotton sheets   | 29.95 | True      | HOUSEWARES |

  Scenario: Read a Product
    When I visit the "Home Page"
    And I set the "Name" to "Hat"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Hat" in the "Name" field
    And I should see "A red fedora" in the "Description" field
    When I copy the "ID" field
    And I press the "Clear" button
    And I paste the "ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Hat" in the "Name" field
    And I should see "A red fedora" in the "Description" field
    And I should see "59.95" in the "Price" field
    And I should see "True" in the "Available" dropdown
    And I should see "Cloths" in the "Category" dropdown

  Scenario: Update a Product
    When I visit the "Home Page"
    And I set the "Name" to "Hat"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Hat" in the "Name" field
    And I should see "A red fedora" in the "Description" field
    When I change "Name" to "Fedora"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "ID" field
    And I press the "Clear" button
    And I paste the "ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Fedora" in the "Name" field
    And I should see "A red fedora" in the "Description" field
    When I press the "Clear" button
    And I set the "Name" to "Fedora"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Fedora" in the results
    And I should not see "Hat" in the results

  Scenario: Delete a Product
    When I visit the "Home Page"
    And I set the "Name" to "Hat"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Hat" in the "Name" field
    And I should see "A red fedora" in the "Description" field
    When I copy the "ID" field
    And I press the "Delete" button
    Then I should see the message "Product has been Deleted!"
    When I press the "Clear" button
    And I paste the "ID" field
    And I press the "Retrieve" button
    Then I should see the message "Product was not found"
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should not see "Hat" in the results
    And I should see "Shoes" in the results

  Scenario: List all Products
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Hat" in the results
    And I should see "Shoes" in the results
    And I should see "Big Mac" in the results
    And I should see "Sheets" in the results

  Scenario: Search for Products by Category
    When I visit the "Home Page"
    And I select "Cloths" in the "Category" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Hat" in the results
    And I should see "Shoes" in the results
    And I should not see "Big Mac" in the results
    And I should not see "Sheets" in the results

  Scenario: Search for Products by Availability
    When I visit the "Home Page"
    And I select "True" in the "Available" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Hat" in the results
    And I should see "Big Mac" in the results
    And I should see "Sheets" in the results
    And I should not see "Shoes" in the results

  Scenario: Search for a Product by Name
    When I visit the "Home Page"
    And I set the "Name" to "Hat"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Hat" in the "Name" field
    And I should see "A red fedora" in the "Description" field
    And I should see "Hat" in the results
    And I should not see "Shoes" in the results
    And I should not see "Big Mac" in the results
    And I should not see "Sheets" in the results
