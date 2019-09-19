# Manual Search Usage

Each search query will be comprised of *up to* 5 parts, depending on the supported [*search type*](./manualsearch.md#search-types-and-their-capabilities):
- `Site` - Either the shorthand abbreviation, or full site name.
- `Date` - Follows immediately after site name, in the format of either `YYYY-MM-DD` or `YY-MM-DD` ([more on how this can be used](./manualsearch.md#search-types-and-their-capabilities))
- `Actor(s)`
- `Title` - The title/name of the scene.
- `SceneID` - A numeric value found in the URL of a scene. ([more on how this can be used](./manualsearch.md#search-types-and-their-capabilities))
- `Direct URL` - A string of characters at the end of a URL. Typically includes some combination of a SceneID, Scene Title, or Actor.

# Search types and their capabilities
There are 3 available search/matching methods, as listed below:
+ **Enhanced Search:** `Title` `Actor` `Date` `SceneID`
+ **Limited Search:** `Title` `Actor`
+ **Exact Match:** `SceneID` `Direct URL`

## Enhanced Search
#### Multi-search available.
+ **Available search methods**
  - **Title**
  - **Actor(s)**
+ **Available match methods**
*These can be used in conjunction with available search methods and will increase the possibility of locating the correct scene. However, they cannot be used as standalone search terms. At least one of these can be utilized, depending on the site.*
  - **Date**
  - **SceneID** 

+ **SceneID Match:** SceneID can be entered as a search term alongside other search terms (Title, Actor) to increase the possibility for a match, but cannot be entered as a standalone search term.
  - Example: Though Kink has a full-fledged title/actor search function, you cannot enter just a SceneID and find results. However, if a SceneID is entered alongside a title/actor, it will increase the possibility of locating the correct scene
+ **Date Match:** Date can be entered alongside other search terms to improve search results

## Limited Search
#### Limited-search available.
+ Available search methods:
  - **Title**
  - **Actor**

## Exact Match
#### No search available.
*Locating the correct scene is entirely dependent on entering the correct SceneID or Direct URL. In some cases, you may add additional terms to your search. However, these will not increase the possibility of locating the correct scene and are only implemented for convenience.*
+ **SceneID**
  - Can add the the Date (before the SceneID)
  - Can typically add a Title/Actor (after the SceneID).
+ **Direct URL**
  - Can add the the Date (before the URL)
  - Adding any terms, such as Title/Actors, after the URL will cause issues with matching.

## Notes
+ **Date Add** - Some sites don't make release dates available, so the agent will strip the date from your filename/search term instead

# Search Examples
Depending on the capability of any one network/site, you can try a few combiations of the above.

Here are some examples for each type of search:
+ **Enhanced Search** examples:
  - A full search, with all available details:
    - `SiteName` `YY-MM-DD` `SceneID` `Jane Doe` `An Interesting Plot`
  - A minimal search, with fewer details, but includes SceneID:
    - `SiteName` `SceneID` `Jane Doe`
  - A basic search with the most common details:
    - `SiteName` `Jane Doe` `An Interesting Plot`
  - Another minimal search, using the site shorthand:
    - `SN` `An Interesting Plot`
  
+ **Limited Search** examples:
  - A search using both actor and scene title:
    - `SiteName` `Jane Doe` `An Interesting Plot`
  - A search using site name and an actor from the scene:
    - `SiteName` `Jane Doe`
  - A search using site shorthand with the scene title:
    - `SN` `An Interesting Plot`
    
+ **Exact Match** examples:
  - An exact search using site name and ID:
    - `SiteName` `SceneID`
  - An exact search using site shorthand and ID:
    - `SN` `SceneID`
  - A direct url match, using only a suffix:
    - `SiteName` `Direct URL`
      - `PornPros` `eager-hands` (taken from the URL [https://pornpros.com/video/**eager-hands**](https://pornpros.com/video/eager-hands))
    - `SiteName` `YY-MM-DD` `Direct URL`
      - `Mylf` `2019.01.01` `1809 manicured-milf-masturbation` (taken from the URL [https://www.mylf.com/movies/**1809/manicured-milf-masturbation**](https://www.mylf.com/movies/1809/manicured-milf-masturbation))
