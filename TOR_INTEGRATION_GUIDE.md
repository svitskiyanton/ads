# Tor IP Changing Integration Guide

## 🌐 Overview

The Orbita Form Filler now includes integrated **Tor IP changing** functionality based on the [isPique/Tor-IP-Changer](https://github.com/isPique/Tor-IP-Changer) project. This helps avoid detection and IP blocking when posting multiple ads.

## 🔧 Features

- **Cross-platform**: Works on both Windows and Linux/Unix systems
- **Automatic Tor management**: Downloads, installs, and manages Tor automatically
- **Browser proxy integration**: Configures Playwright to route traffic through Tor
- **Configurable IP rotation**: Change IP every N ads or disable entirely
- **IP verification**: Checks current IP address through Tor network
- **Graceful cleanup**: Properly stops Tor service when finished

## ⚙️ Configuration

### Config Settings (config.py)

```python
# Tor IP Changing settings
USE_TOR_IP_ROTATION = True  # Enable/disable Tor IP rotation
TOR_IP_CHANGE_INTERVAL = 3  # Change IP every N ads (set to 1 for every ad, 0 to disable)
TOR_STARTUP_DELAY = 5       # Seconds to wait after starting Tor
TOR_IP_CHANGE_DELAY = 3     # Seconds to wait after changing IP
```

### Tor Path Configuration

- **Windows**: Uses `tor_path.txt` file (defaults to `C:\`)
- **Linux**: Uses system package manager (apt)

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
pip install requests[socks]
```

### 2. Configure Settings

Edit `config.py`:
```python
USE_TOR_IP_ROTATION = True
TOR_IP_CHANGE_INTERVAL = 3  # Change IP every 3 ads
```

### 3. Test Integration

```bash
python test_tor_integration.py
```

### 4. Run with Tor

```bash
python orbita_form_filler.py
```

## 🖥️ Platform-Specific Setup

### Windows
- Tor will be automatically downloaded from official sources
- Extracts to `C:\Tor Expert Bundle\` by default
- Manages Tor process using `tasklist` and `taskkill`

### Linux/Unix
- Requires root privileges: `sudo python3 orbita_form_filler.py`
- Installs Tor via: `sudo apt install tor`
- Manages via system service: `sudo service tor start/stop/reload`

## 🔄 How IP Changing Works

1. **Initialization**: 
   - Downloads/installs Tor if needed
   - Starts Tor service on port 9050
   - Configures SOCKS5 proxy

2. **Browser Integration**:
   - Playwright configured with proxy: `socks5://127.0.0.1:9050`
   - All browser traffic routes through Tor network

3. **IP Rotation**:
   - **Linux**: `sudo service tor reload`
   - **Windows**: Kill and restart tor.exe process
   - Verifies new IP via `https://httpbin.org/ip`

4. **Cleanup**:
   - Stops Tor service when script finishes
   - Removes temporary files

## 📊 Workflow Integration

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Start Script    │───▶│ Initialize Tor  │───▶│ Check Current IP│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Process Ad 1    │◄───│ Start Browser   │◄───│ Configure Proxy │
└─────────────────┘    │ with Tor Proxy  │    └─────────────────┘
          │             └─────────────────┘             
          ▼                                              
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Process Ad 2    │───▶│ Process Ad 3    │───▶│ Change IP?      │
└─────────────────┘    └─────────────────┘    │ (every N ads)   │
          │                      │             └─────────────────┘
          │                      │                      │
          │                      │             ┌─────────────────┐
          │                      └────────────▶│ Change Tor IP   │
          │                                    └─────────────────┘
          ▼                                             │
┌─────────────────┐    ┌─────────────────┐              │
│ Continue...     │◄───│ Verify New IP   │◄─────────────┘
└─────────────────┘    └─────────────────┘              
          │                                              
          ▼                                              
┌─────────────────┐                                     
│ Stop Tor        │                                     
│ & Cleanup       │                                     
└─────────────────┘                                     
```

## 🛡️ Security Benefits

1. **IP Anonymization**: Routes traffic through Tor network
2. **Reduced Detection**: Different IP for each batch of ads  
3. **Anti-Blocking**: Avoids rate limiting and IP bans
4. **Geographic Diversity**: IPs from different locations
5. **Traffic Obfuscation**: Makes automation less obvious

## ⚠️ Important Notes

### Performance Impact
- **Slower browsing**: Tor adds latency to requests
- **Connection timeouts**: May need increased timeout values
- **Variable speeds**: Tor circuit quality varies

### System Requirements
- **Windows**: No admin rights needed (downloads to user folder)
- **Linux**: Requires sudo for service management
- **Network**: Outbound access to Tor network (port 9001, 9030)

### Troubleshooting

#### Tor Won't Start
```bash
# Linux: Check service status
sudo service tor status

# Windows: Check if port 9050 is blocked
netstat -an | find "9050"
```

#### IP Not Changing
```bash
# Test IP directly
curl --proxy socks5://127.0.0.1:9050 https://httpbin.org/ip
```

#### Download Issues
- Check firewall settings
- Verify internet connectivity
- Try manual Tor installation

## 🧪 Testing

### Test Script Features
```bash
python test_tor_integration.py
```

Tests:
- ✅ Tor initialization
- ✅ Service startup  
- ✅ IP address checking
- ✅ IP changing functionality
- ✅ Browser proxy configuration
- ✅ Website access through Tor

### Manual Testing
1. Run test script
2. Check IP before: `curl https://httpbin.org/ip`
3. Start Tor integration
4. Check IP after: `curl --proxy socks5://127.0.0.1:9050 https://httpbin.org/ip`

## 📋 Configuration Examples

### Conservative (Change IP rarely)
```python
USE_TOR_IP_ROTATION = True
TOR_IP_CHANGE_INTERVAL = 10  # Every 10 ads
TOR_STARTUP_DELAY = 10       # Extra startup time
TOR_IP_CHANGE_DELAY = 5      # Extra change delay
```

### Aggressive (Change IP frequently)
```python
USE_TOR_IP_ROTATION = True
TOR_IP_CHANGE_INTERVAL = 1   # Every ad
TOR_STARTUP_DELAY = 3        # Minimal delays
TOR_IP_CHANGE_DELAY = 2      
```

### Disabled (No Tor)
```python
USE_TOR_IP_ROTATION = False  # Use regular connection
```

## 🎯 Best Practices

1. **Test first**: Always run `test_tor_integration.py` before production
2. **Monitor logs**: Watch for IP change confirmations
3. **Reasonable intervals**: Don't change IP too frequently (creates suspicion)
4. **Backup plan**: Have fallback without Tor if issues arise
5. **Network monitoring**: Ensure Tor traffic is allowed by firewall

## 🔗 References

- [Original Tor IP Changer](https://github.com/isPique/Tor-IP-Changer)
- [Tor Project Official](https://www.torproject.org/)
- [Playwright Proxy Documentation](https://playwright.dev/docs/network#http-proxy)
- [SOCKS5 Proxy Protocol](https://tools.ietf.org/html/rfc1928) 