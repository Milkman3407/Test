import unittest

from NetworkTool.network_interface_manager import netsh_name_arg, parse_interfaces


class TestNetworkInterfaceManager(unittest.TestCase):
    def test_parse_interfaces_skips_headers_and_parses_names_with_spaces(self) -> None:
        raw = (
            "Admin State    State          Type             Interface Name\n"
            "-------------------------------------------------------------------------\n"
            "Enabled        Connected      Dedicated        Ethernet\n"
            "Enabled        Disconnected   Dedicated        Wi-Fi Adapter 2\n"
            "Disabled       Disconnected   Dedicated        USB LAN\n"
        )

        adapters = parse_interfaces(raw)

        self.assertEqual(len(adapters), 3)
        self.assertEqual(adapters[1].name, "Wi-Fi Adapter 2")
        self.assertEqual(adapters[2].state, "Disconnected")

    def test_netsh_name_arg_quotes_interface_name(self) -> None:
        self.assertEqual(netsh_name_arg("Ethernet 2"), 'name="Ethernet 2"')

    def test_netsh_name_arg_escapes_double_quotes(self) -> None:
        self.assertEqual(netsh_name_arg('Corp "LAN" Adapter'), 'name="Corp \\\"LAN\\\" Adapter"')


if __name__ == "__main__":
    unittest.main()
