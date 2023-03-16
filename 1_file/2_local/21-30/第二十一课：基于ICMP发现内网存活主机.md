# 专注APT攻击与防御
https://micropoor.blogspot.com/

**ICMP简介：**
它是TCP/IP协议族的一个子协议，用于在IP主机、路由器之间传递控制消息。控制消息是指网络通不通、主机是否可达、路由是否可用等网络本身的消息。这些控制消息虽然并不传输用户数据，但是对于用户数据的传递起着重要的作用。

**nmap扫描：**
```bash
root@John:~# nmap ‐sP ‐PI 192.168.1.0/24 ‐T4
```


![](D:\work\wiki\wiki\1_file\2_local\21-30\image\第二十一课：基于ICMP发现内网存活主机\image-09fa7abb-ea52-4159-8f06-099ab8e34d38.jpg)


```bash
root@John:~# nmap ‐sn ‐PE ‐T4 192.168.1.0/24
```


![](D:\work\wiki\wiki\1_file\2_local\21-30\image\第二十一课：基于ICMP发现内网存活主机\image-85fc77be-1e46-45b4-89e5-e8a051049965.jpg)


**CMD下扫描：**
```bash
for /L %P in (1,1,254) DO @ping ‐w 1 ‐n 1 192.168.1.%P | findstr "TTL ="
```


![](D:\work\wiki\wiki\1_file\2_local\21-30\image\第二十一课：基于ICMP发现内网存活主机\image-50922554-ffd7-43bd-8e3f-e0f9033b8e8d.jpg)


**powershell扫描：**
```powershell
powershell.exe ‐exec bypass ‐Command "Import‐Module ./Invoke‐TSPingSweep.ps1
; Invoke‐TSPingSweep ‐StartAddress 192.168.1.1 ‐EndAddress 192.168.1.254 ‐Resolv
eHost ‐ScanPort ‐Port 445,135"
```


![](D:\work\wiki\wiki\1_file\2_local\21-30\image\第二十一课：基于ICMP发现内网存活主机\image-b08fde36-c670-44ca-86b4-37cc93fe2b67.jpg)




![](D:\work\wiki\wiki\1_file\2_local\21-30\image\第二十一课：基于ICMP发现内网存活主机\image-873da42b-7c7e-4d21-aad4-1461a36d949c.jpg)


```bash
D:\>tcping.exe ‐n 1 192.168.1.0 80
```


![](D:\work\wiki\wiki\1_file\2_local\21-30\image\第二十一课：基于ICMP发现内网存活主机\image-fc91f48b-06f2-406b-99fb-b208566a5d42.jpg)


**附录:**
powershell脚本与tcping（来源互联网，后门自查）
链接：https://pan.baidu.com/s/1dEWUBNN 密码：9vge

>   Micropoor
