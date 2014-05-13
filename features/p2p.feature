Feature: Websocket Client Interface

  Scenario: Connection
    Given there is a node
     When we connect
     Then it will introduce itself 

  Scenario: Connect to a node
    Given there are two nodes
    When a node connects to another
    Then they will have each other as peers
