const settingsbutton = document.getElementById("settingsbutton")
const settings = document.getElementById("settings")
const isFireFox = typeof InstallTrigger !== 'undefined'
let justToggled = false

sessionSettings = Object(sessionSettings)

settingsbutton.addEventListener("click", () => toggleSettings())
currentFav = document.querySelector(`[value='${sessionSettings?.fav}']`)

if (currentFav) {
    currentFav.classList.add("checked")
}

const settingsFav = Array.from(document.getElementsByName("settingfav"))
settingsFav.forEach(elem => elem.addEventListener("click", () => clickSettingFav(elem)))

const filedrop = document.getElementById("filedrop")

Array.from(["dragenter", "dragover", "dragleave", "drop"]).forEach(eventName => {
      filedrop.addEventListener(eventName, e => e.preventDefault());
      document.body.addEventListener(eventName, e => e.preventDefault());
})

filedrop.addEventListener("dragover", e => {
    e.preventDefault()
    filedrop.classList.add("dragover")
})

filedrop.addEventListener("dragleave", e => {
    e.preventDefault()
    filedrop.classList.remove("dragover")
})

if (isFireFox){
        filedrop.innerHTML = `<b>Drop scores.db to import local scores.</b><br>This feature is bugged on FireFox. Try a chromium-based browser.`
    }

filedrop.addEventListener("drop", (e) => {
    e.preventDefault()
    e.stopPropagation()
    filedrop.classList.remove("dragover")
    if (isFireFox){
        return
    }

    const files = e.dataTransfer.files
    const db = files[0]
    const formData = new FormData()
    formData.append("db", db)
    formData.append("uid", sessionID)
    formData.append("discord_uid", sessionSettings.discord_uid)
    fetch("/auth/upload_scores_db", {
        method: "POST",
        body: formData,
    })
    .then(async response => {
        const resp = await response.json()
        if (!response.ok) { throw resp }
        return resp
    })
    .then(data => {
        filedrop.innerHTML = `<b>Drop scores.db to import local scores.</b><br>${data.message}`
    })
    .catch(e => {
        filedrop.innerHTML = `<b>Drop scores.db to import local scores.</b><br>Error: ${e.error}`
    })
})

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