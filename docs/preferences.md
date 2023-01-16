# Preferences Definitions

## Male Actor Filter
 - Enable/Disable the adding of Male Actors

## Remove Obsolete Images
 - Enable/Disable removal of images no longer found in scrape from metadata when running the "Refresh Metadata" Operation

## Remove Stored Images
 - Enable/Disable removal of all stored images from metadata when running the "Refresh Metadata" Operation
 - Can be used to address images persisting after a mismatch

## Prevent Automatic Matching
 - Enable/Disable manual override of automatic matching when running the "Scan Library" Operation
 - Large library additions may result in some scrapers to IP BAN (i.e. Data18)

## MetadataAPI
 - Enable/Disable fallback to https://metadataapi.net/ for matching

## MetadataAPI Token
 - API Token for MetadataAPI https://metadataapi.net/user/api-tokens

## Enable FileName Strip
 - Enable/Disable strip text before/after a specified symbol

## FileName Strip After Symbol
 - Strip text after provided symbol for FileName Strip
 - Default: ~

## FileName Strip Before Symbol
 - Strip text before provided symbol for FileName Strip
 - Default: %

## Use Custom Title Format
 - Enable/Disable custom title format

## Custom Title Format
 - {title} - Title
 - {actors} - Actors in comma separated list
 - {studio} - Studio
 - {series} - Collections in comma separated list
 - Default: {actors} - {title} [{studio}/{series}]

## Enable Custom Order for Actor Matching
 - Enable/Disable a custom order for Actor metadata

## Custom Order for Actor Matching
 - Allows for ranking perferred actor metadata source
 - Default: Local Storage, Freeones, IAFD, Indexxx, AdultDVDEmpire, Boobpedia, Babes and Stars, Babepedia

## Proxy Preferences

 * ### Proxy Enable
   - Enable/Disable Proxy for HTTP Requests

 * ### Proxy Type
   - Sets Proxy Type
   - Options
     - http
     - https
     - socks4
     - socks4a
     - socks5
     - socks5h
   - Default: socks5

 * ### Proxy IP
   - IP Address for Proxy
   - Default: 127.0.0.1

 * ### Proxy Port
   - Port for Proxy
   - Default: 9050

 * ### Enable Proxy Authentication
   - Enable/Disable Authentication for Proxy

 * ### Proxy Username
   - Username required for Proxy Auth

 * ### Proxy Password
   - Password required for Proxy Auth

## Anti-Scrape Tools
 - Some sites employ anti-scrape technoligies which can block matches. These services and tools can be used to bypass some restrictions.
 - FlareSolverr Endpoint URL (self hosted)
   - FlareSolverr is a proxy server to bypass Cloudflare and DDoS-GUARD protection.
   - For more information and how to set up see https://github.com/FlareSolverr/FlareSolverr
 - Enable Captcha Based Solvers
   - Enable/Disable automated captcha solver
   - Requires Paid Service
 - Captcha Solver Service
   - Sets desired Captcha Solver Service
   - Options
     - anticaptcha - https://anti-captcha.com/
     - 2captcha - https://2captcha.com/
     - 9kw - http://www.9kw.eu/
   - Default: 9kw
 - Captcha API Key
   - API Key Provided by the set Captcha Service
