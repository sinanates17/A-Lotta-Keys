const settingsbutton = document.getElementById("settingsbutton")
const settings = document.getElementById("settings")
let justToggled = false

sessionSettings = Object(sessionSettings)

settingsbutton.addEventListener("click", () => toggleSettings())
currentFav = document.querySelector(`[value='${sessionSettings?.fav}']`)

if (currentFav) {
    currentFav.classList.add("checked")
}

const settingsFav = Array.from(document.getElementsByName("settingfav"))
settingsFav.forEach(elem => elem.addEventListener("click", () => clickSettingFav(elem)))

function clickSettingFav(elem) {
    if (elem.classList.contains("checked")) {
        elem.classList.remove("checked")
        val = ""
    }

    else {
        settingsFav.forEach(e => {
            e.classList.remove("checked")
        })

        elem.classList.add("checked")
        val = elem.value
    }

    const payload = {
        id: sessionID,
        settingFav: val
    }

    fetch('/auth/setting_fav', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
})

}

function toggleSettings() {
    settings.classList.toggle("active")

    if (settings.classList.contains("active")) {
        document.addEventListener("click", settingsEventListenerCallback)
        justToggled = true
    }

    if (!settings.classList.contains("active")) {
        document.removeEventListener("click", settingsEventListenerCallback)
    }
}

function settingsEventListenerCallback(event) {
    if (justToggled) {
        justToggled = false
        return
    }
    if (!settings.contains(event.target) && settings.classList.contains("active")) { 
        toggleSettings()}
}