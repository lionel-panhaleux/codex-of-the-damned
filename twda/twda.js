async function getDeck(data) {
    let response = await fetch(
        `https://krcg.herokuapp.com/deck`, {
        method: "post",
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    }
    )
    let result = await response.json()
    return result
}
function displayError(message) {
    document.getElementById("results").textContent = message
}
function cardElement(element) {
    let reference = element[1].toLowerCase()
    if (reference.startsWith("the ")) {
        reference = reference.substr(4, reference.length) + "the"
    }
    reference = reference.replace(/\s|,|\.|-|'|:|\(|\)|"|!/g, "")
    reference = reference.replace("é", "e") // Céleste
    reference = reference.replace("ö", "o") // Rötschreck
    reference = reference.replace("ç", "c") // Monçada
    reference = reference.replace("ó", "o") // Dónal
    const name = element[1].replace("(TM) ", "™ ")
    return `<li>${element[0]} <span class="card" onclick="dC('${reference}')">${name}</span></li>\n`
}
function wrapText(text, maxlen) {
    if (!text) {
        return "N/A"
    }
    if (text.length > maxlen) {
        return text.substr(0, maxlen - 3) + "..."
    }
    return text
}
function removeComments() {
    comments.innerHTML = ""
}
function displayDeck(data, twda_id) {
    removeComments()
    document.getElementById("deck-link").textContent = wrapText(data["name"], 25)
    document.getElementById("deck-link").href = `http://www.vekn.fr/decks/twd.htm#${twda_id}`
    document.getElementById("deck-header").innerHTML = [
        data["player"],
        wrapText(data["event"], 40),
        wrapText(data["place"], 40),
        data["date"],
        data["players_count"] + " players",
    ].join("<br/>")
    document.getElementById("crypt-header").textContent = `Crypt (${data["crypt"][0]})`
    data["crypt"][1].map(cardElement).join("\n")
    document.getElementById("crypt-list").innerHTML = data["crypt"][1].map(cardElement).join("\n")
    document.getElementById("library-header").textContent = `Library (${data["library"][0]})`
    card_list = ""
    const TYPE_ORDER = [
        "Master",
        "Conviction",
        "Action",
        "Action/Combat",
        "Action/Reaction",
        "Political Action",
        "Action Modifier",
        "Action Modifier/Reaction",
        "Action Modifier/Combat",
        "Combat",
        "Combat/Action",
        "Combat/Action Modifier",
        "Combat/Reaction",
        "Reaction",
        "Reaction/Action Modifier",
        "Reaction/Combat",
        "Power",
        "Equipment",
        "Ally",
        "Retainer",
        "Event",
    ]
    types = Object.entries(data["library"][1]).sort(
        (a, b) => TYPE_ORDER.indexOf(a[0]) - TYPE_ORDER.indexOf(b[0])
    )
    for (let [type, cards] of types) {
        card_list += `<li><h4>— ${type} (${cards[0]}) —</h4></li>`
        for (const element of cards[1]) {
            card_list += cardElement(element)
        }
    }
    document.getElementById("library-list").innerHTML = card_list
    comments = document.getElementById("comments")
    for (let section of data["comments"].split("\n\n")) {
        pelem = document.createElement("p")
        pelem.textContent = section
        comments.appendChild(pelem)
    }
    document.getElementById("decklist").style.display = "block"
    document.getElementById("comments-title").style.display = "block"
}
function getAndDisplayDeck(element, twda_id) {
    getDeck({ "twda_id": twda_id })
        .then(data => displayDeck(data[0][1], data[0][0]))
        .catch(reason => displayError(reason.message))
    if (element) {
        window.history.pushState({ "twda_id": 1 }, "TWDA", `?twda_id=${twda_id}`)
        for (let sibling of element.parentElement.children) {
            sibling.classList.remove("selected")
        }
        element.classList.add("selected")
    }
}
function displayDeckChoices(data) {
    removeComments()
    let list = ""
    if (!data || data.length < 1) {
        list = "No result in TWDA."
    }
    for (const [twda_id, deck] of data) {
        list += `
        <tr class="results">
            <td class="results date" onclick="getAndDisplayDeck(this.parentNode, '${twda_id}')">${deck["date"]}</td>
            <td class="results player" onclick="getAndDisplayDeck(this.parentNode, '${twda_id}')">${deck["player"]}</td>
            <td class="results name" onclick="getAndDisplayDeck(this.parentNode, '${twda_id}')">${deck["name"]}</td>
        </tr>
        `
    }
    document.getElementById("results").innerHTML = list
}
async function fetchCompletion(text) {
    let response = await fetch(
        encodeURI(`https://krcg.herokuapp.com/complete/${text}`), {
        method: "GET",
        headers: { 'Accept': 'application/json' }
    }
    )
    let result = await response.json()
    return result
}
function clearSearch() {
    document.getElementById("decklist").style.display = "none"
    document.getElementById("comments-title").style.display = "none"
    document.getElementById("results").innerHTML = ""
    removeComments()
}
function autocomplete(element) {
    var currentFocus
    function doComplete(e) {
        const val = this.value
        closeAllLists();
        if (!val || val.length < 3) {
            clearSearch()
            return false
        }
        currentFocus = -1
        let a = document.createElement("DIV")
        a.setAttribute("id", this.id + "autocomplete-list")
        a.setAttribute("class", "autocomplete-items")
        this.parentNode.appendChild(a)
        fetchCompletion(val)
            .then(function (result) {
                console.log(result)
                for (const candidate of result) {
                    let b = document.createElement("DIV")
                    b.textContent = candidate
                    b.addEventListener("click", function (e) {
                        element.value = this.textContent
                        closeAllLists()
                        getDeck({ "cards": [element.form.card_name.value] })
                            .then(data => displayDeckChoices(data))
                            .catch(reason => displayError(reason.message))
                    })
                    a.appendChild(b);
                }
            })
            .catch(reason => displayError(reason.message))
    }
    element.addEventListener("input", doComplete)
    element.addEventListener("keydown", function (e) {
        let x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode === 40) { // arrow DOWN
            currentFocus++;
            addActive(x);
        } else if (e.keyCode === 38) { // arrow UP
            currentFocus--;
            addActive(x);
        } else if (e.keyCode === 13) { // ENTER
            e.preventDefault();
            if (currentFocus > -1 && x) { x[currentFocus].click() }
            getDeck({ "cards": [element.form.card_name.value] })
                .then(data => displayDeckChoices(data))
                .catch(reason => displayError(reason.message))
        } else if (e.keyCode === 8 || e.keyCode === 46) { // DELETE or BACKSPACE
            doComplete()
        }
    });
    function addActive(x) {
        if (!x) { return false }
        for (child of x) { child.classList.remove("autocomplete-active") }
        if (currentFocus >= x.length) { currentFocus = 0 }
        if (currentFocus < 0) { currentFocus = (x.length - 1) }
        x[currentFocus].classList.add("autocomplete-active");
    }
    function closeAllLists(elmnt) {
        for (let x of document.getElementsByClassName("autocomplete-items")) {
            if (elmnt != x && elmnt != element) { x.parentNode.removeChild(x) }
        }
    }
    document.addEventListener("click", function (e) {
        closeAllLists(e.target)
    });
}
function displayDeckFromURL() {
    const urlParams = new URLSearchParams(window.location.search)
    if (urlParams.has("twda_id")) {
        getAndDisplayDeck(null, urlParams.get("twda_id"))
    }
    else {
        clearSearch()
    }
}
window.onload = function () {
    autocomplete(document.getElementById("card_name"))
    displayDeckFromURL()
    window.onpopstate = displayDeckFromURL
}