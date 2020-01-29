function getDeckWithCards(cards) {
    fetch(
        `https://krcg.herokuapp.com/deck`, {
        method: "POST",
        body: JSON.stringify({ "cards": cards }),
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    })
        .then(function (response) {
            if (!response.ok) {
                throw Error(response.statusText);
            }
            return response;
        })
        .then(response => response.json())
        .then(data => displayDeckChoices(data))
        .catch(function (error) {
            document.getElementById("results").textContent = error.message
        })
}
function getDeckByID(element, twda_id) {
    fetch(
        encodeURI(`https://krcg.herokuapp.com/deck/${twda_id}`), {
        method: "GET",
        headers: { 'Accept': 'application/json' }
    })
        .then(function (response) {
            if (!response.ok) {
                throw Error(response.statusText);
            }
            return response;
        })
        .then(response => response.json())
        .then(data => displayDeck(data))
        .catch(function (error) {
            document.getElementById("results").textContent = error.message
        })
    if (element) {
        window.history.pushState({ "twda_id": twda_id }, "TWDA", `?twda_id=${twda_id}`)
        for (let sibling of element.parentElement.children) {
            sibling.classList.remove("selected")
        }
        element.classList.add("selected")
    }
}
function cardElement(element) {
    let reference = element["name"].toLowerCase()
    if (reference.startsWith("the ")) {
        reference = reference.substr(4, reference.length) + "the"
    }
    reference = reference.replace(/\s|,|\.|-|'|:|\(|\)|"|!/g, "")
    reference = reference.replace(/é/g, "e") // Céleste
    reference = reference.replace(/ö|ó/g, "o") // Rötschreck, Dónal
    reference = reference.replace(/ç/g, "c") // Monçada
    reference = reference.replace(/á/g, "a") // Vásquez
    reference = reference.replace(/ñ/g, "n") // Montaña
    const name = element["name"].replace("(TM) ", "™ ")
    return `<li>${element["count"]} <span class="card" onclick="dC('${reference}')">${name}</span></li>\n`
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
function displayDeck(data) {
    removeComments()
    document.getElementById("deck-link").textContent = wrapText(data["name"], 25)
    document.getElementById("deck-link").href = `http://www.vekn.fr/decks/twd.htm#${data["twda_id"]}`
    document.getElementById("deck-header").innerHTML = [
        wrapText(data["player"], 40),
        wrapText(data["event"], 40),
        wrapText(data["place"], 40),
        data["date"],
        data["players_count"] + " players",
    ].join("<br/>")
    document.getElementById("crypt-header").textContent = `Crypt (${data["crypt"]["count"]})`
    data["crypt"]["cards"].map(cardElement).join("\n")
    document.getElementById("crypt-list").innerHTML = data["crypt"]["cards"].map(cardElement).join("\n")
    document.getElementById("library-header").textContent = `Library (${data["library"]["count"]})`
    card_list = ""
    for (const section of data["library"]["cards"]) {
        card_list += `<li><h4>— ${section["type"]} (${section["count"]}) —</h4></li>`
        for (const element of section["cards"]) {
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
function displayDeckChoices(data) {
    console.log(data)
    removeComments()
    let list = ""
    if (!data || data.length < 1) {
        list = "No result in TWDA."
    }
    for (const deck of data) {
        list += `
        <tr class="results">
            <td class="results date" onclick="getDeckByID(this.parentNode, '${deck["twda_id"]}')">${deck["date"]}</td>
            <td class="results player" onclick="getDeckByID(this.parentNode, '${deck["twda_id"]}')">${wrapText(deck["player"], 40)}</td>
            <td class="results name" onclick="getDeckByID(this.parentNode, '${deck["twda_id"]}')">${wrapText(deck["name"], 80)}</td>
        </tr>
        `
    }
    document.getElementById("results").innerHTML = list
}
function displayCompletion(input, items_list, data) {
    for (const candidate of data) {
        let b = document.createElement("DIV")
        b.textContent = candidate
        b.addEventListener("click", function (e) {
            input.value = this.textContent
            closeAllLists(input)
            getDeckWithCards([input.value])
        })
        items_list.appendChild(b);
    }
}
function fetchCompletion(input, items_list, text) {
    fetch(
        encodeURI(`https://krcg.herokuapp.com/complete/${text}`), {
        method: "GET",
        headers: { 'Accept': 'application/json' }
    })
        .then(function (response) {
            if (!response.ok) {
                throw Error(response.statusText);
            }
            return response;
        })
        .then(response => response.json())
        .then(data => displayCompletion(input, items_list, data))
        .catch(function (error) {
            document.getElementById("results").textContent = error.message
        })
}
function clearSearch() {
    document.getElementById("decklist").style.display = "none"
    document.getElementById("comments-title").style.display = "none"
    document.getElementById("results").innerHTML = ""
    removeComments()
}
function autocomplete(input) {
    var currentFocus
    function doComplete(e) {
        const val = this.value
        closeAllLists(input);
        if (!val || val.length < 3) {
            clearSearch()
            return false
        }
        currentFocus = -1
        let items_list = document.createElement("DIV")
        items_list.setAttribute("id", this.id + "autocomplete-list")
        items_list.setAttribute("class", "autocomplete-items")
        this.parentNode.appendChild(items_list)
        fetchCompletion(input, items_list, val)
    }
    input.addEventListener("input", doComplete)
    input.addEventListener("keydown", function (e) {
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
            getDeckWithCards([input.value])
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
    document.addEventListener("click", function (e) {
        closeAllLists(input, e.target)
    });
}
function closeAllLists(input, elmnt) {
    for (let x of document.getElementsByClassName("autocomplete-items")) {
        if (elmnt != x && elmnt != input) { x.parentNode.removeChild(x) }
    }
}
function displayDeckFromURL() {
    const urlParams = new URLSearchParams(window.location.search)
    if (urlParams.has("twda_id")) {
        getDeckByID(null, urlParams.get("twda_id"))
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