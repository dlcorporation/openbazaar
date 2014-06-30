Feature: CryptoTransportLayer

  Scenario: Connecting 2 peers
    Given 2 layers
    When layer 0 connects to layer 1
    Then layer 0 is aware of layer 1

  Scenario: Connecting 3 peers
    Given 3 layers
    When layer 0 connects to layer 1
    and layer 1 connects to layer 2
    Then layer 0 is aware of layer 1
    and layer 1 is aware of layer 2