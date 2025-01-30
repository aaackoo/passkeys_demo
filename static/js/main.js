async function getUser() {
    const response = await fetch("/check_login");
    const data = await response.json();

    if (!response.ok) {
        alert(`Unidentified error: ${response.status} - ${response.statusText}`);
        throw new Error(`Server returned ${response.status} - ${response.statusText}`);
    }

    if (data.logged_in) {
        return {case: true, data: data.user}
    } else {
        return {case: false, data: "please register/login below"}
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    console.log("geno");
    const heading = document.querySelector("h2");
    const logoutBtn = document.getElementById("logoutBtn");

    const x = await getUser();

    if (x.case) {
        logoutBtn.style.display = "block";
    } else {
        logoutBtn.style.display = "none";
    }

    heading.textContent = `${x.data}!`;
});