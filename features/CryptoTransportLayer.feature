Feature: CryptoTransportLayer

  Scenario: Connecting 2 peers
    Given 2 layers
    When layer 0 connects to layer 1
    Then layer 0 is aware of layer 1
    And layer 1 is aware of layer 0

  Scenario: Connecting 3 peers
    Given 3 layers
    When layer 0 connects to layer 1
    And layer 1 connects to layer 2
    Then layer 0 is aware of layer 1
    And layer 1 is aware of layer 2

    # the following is not the case
    # and layer 2 is aware of layer 0
