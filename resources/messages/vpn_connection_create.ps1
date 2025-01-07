Add-VpnConnection -Name "2fa.rostelecom-cc.ru VPN" -ServerAddress "2fa.rostelecom-cc.ru" -TunnelType "Ikev2" -AuthenticationMethod eap -SplitTunneling -RememberCredential

Add-VpnConnectionRoute -ConnectionName "2fa.rostelecom-cc.ru VPN" -DestinationPrefix 172.19.224.0/22 -PassThru

Add-VpnConnectionRoute -ConnectionName "2fa.rostelecom-cc.ru VPN" -DestinationPrefix 172.19.16.0/24 -PassThru

Add-VpnConnectionRoute -ConnectionName "2fa.rostelecom-cc.ru VPN" -DestinationPrefix 192.168.199.0/24 -PassThru

Add-VpnConnectionRoute -ConnectionName "2fa.rostelecom-cc.ru VPN" -DestinationPrefix 192.168.96.0/19 -PassThru

Add-VpnConnectionRoute -ConnectionName "2fa.rostelecom-cc.ru VPN" -DestinationPrefix 192.168.128.0/19 -PassThru

Add-VpnConnectionRoute -ConnectionName "2fa.rostelecom-cc.ru VPN" -DestinationPrefix 192.168.160.0/19 -PassThru

Add-VpnConnectionRoute -ConnectionName "2fa.rostelecom-cc.ru VPN" -DestinationPrefix 172.19.0.0/16 -PassThru

Add-VpnConnectionRoute -ConnectionName "2fa.rostelecom-cc.ru VPN" -DestinationPrefix 192.168.196.0/24 -PassThru


$conn = get-vpnconnection -ConnectionName "2fa.rostelecom-cc.ru VPN"
$conn.Routes

$conn
