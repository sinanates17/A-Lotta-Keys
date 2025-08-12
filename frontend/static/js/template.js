const isDev = window.location.hostname === "127.0.0.1";

API_BASE = isDev
  ? "http://127.0.0.1:5000/"
  : "https://alottakeys.xyz/";

document.addEventListener("DOMContentLoaded", function() {

    const logout = document.getElementById("logout")
    const avataricon = document.getElementById("avataricon")
    const login = document.getElementById("login")

    if (logout) {
        const id = Object(sessionID)
        logout.onclick = () => { window.location.href = `${API_BASE}auth/logout` }
        avataricon.onclick = () => { window.location.href = `${API_BASE}api/search/users/${id}` }
    }

    else {
        login.onclick = () => { window.location.href = `${API_BASE}auth/login` }
    }

})