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
                if (response.status >= 500 && response.status < 600) {
                    throw Error("TWDA bootstrapping, please wait...")
                } else if (response.status >= 404 && response.status < 600) {
                    throw Error("No example found in TWDA.")
                }
                else {
                    throw Error(response.statusText)
                }
            }
            return response
        })
        .then(response => response.json())
        .then(data => displayDeckChoices(data))
        .catch(function (error) {
            document.getElementById("result-message").innerHTML = `<p>${error.message}</p>`
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
                if (response.status >= 500 && response.status < 600) {
                    throw Error("TWDA bootstrapping, please wait...")
                } else if (response.status >= 404 && response.status < 600) {
                    throw Error(`Deck #${twda_id} not found.`)
                }
                else {
                    throw Error(response.statusText)
                }
            }
            return response
        })
        .then(response => response.json())
        .catch(function (error) {
            document.getElementById("result-message").innerHTML = `<p>${error.message}</p>`
        })
        .then(data => displayDeck(data))

    if (element) {
        window.history.pushState({ "twda_id": twda_id }, "TWDA", `?twda_id=${twda_id}`)
        for (let sibling of element.parentElement.children) {
            sibling.classList.remove("selected")
        }
        element.classList.add("selected")
    }
}
// function dCi(i) {
//     const card = document.getElementById(`card-${i}`)
//     if (!card) { return }
//     var name = card.textContent.replace("™ ", "(TM) ").toLowerCase()
//     if (name.startsWith("the ")) {
//         name = name.substr(4, name.length) + "the"
//     }
//     name = name.replace(/\s|,|\.|-|'|:|\(|\)|"|!/g, "")
//     name = name.replace(/ö|ó/g, "o") // Rötschreck, Dónal
//     name = name.replace(/ç/g, "c") // Monçada
//     name = name.replace(/é|ë/g, "e") // Céleste, Gaël
//     name = name.replace(/á/g, "a") // Vásquez
//     name = name.replace(/ñ/g, "n") // Montaña
//     name = name.replace(/ü/g, "u") // Powerbase: Zürich
//     document.getElementById(`card-image`).src = '../card-images/'.concat(name, '.jpg');
//     var modal = document.getElementById("card-modal")
//     modal.classList.remove(`modal-card-${i - 1}`);
//     modal.classList.remove(`modal-card-${i + 1}`);
//     modal.classList.add(`modal-card-${i}`)
//     modal.style.display = "block"
//     modal.focus()
// }
// function cardIndex(modal) {
//     for (const c of modal.classList) {
//         if (c.startsWith("modal-card-")) {
//             return parseInt(c.match(/[0-9]+/)[0])
//         }
//     }
// }
// function prevCard(event) {
//     event.stopPropagation()
//     dCi(cardIndex(event.target.parentElement) - 1)
// }
// function nextCard(event) {
//     event.stopPropagation()
//     dCi(cardIndex(event.target.parentElement) + 1)
// }
// function modalKeydown(event) {
//     event.stopPropagation()
//     event.preventDefault();
//     if (event.keyCode === 40) { // arrow DOWN
//         dCi(cardIndex(event.target) + 1)
//     } else if (event.keyCode === 38) { // arrow UP
//         dCi(cardIndex(event.target) - 1)
//     }
// }
// function cardElement(element, i) {
//     const name = element["name"].replace("(TM) ", "™ ")
//     return `<li>${element["count"]} <span class="card" id="card-${i}" onclick="dCi(${i})">${name}</span></li>`
// }
// function wrapText(text, maxlen) {
//     if (!text) {
//         return "(No name)"
//     }
//     if (text.length > maxlen) {
//         return text.substr(0, maxlen - 3) + "..."
//     }
//     return text
// }
// function removeComments() {
//     comments.innerHTML = ""
// }
// function displayDeck(data) {
//     removeComments()
//     document.getElementById("deck-link").textContent = wrapText(data["name"], 25)
//     document.getElementById("deck-link").href = `http://www.vekn.fr/decks/twd.htm#${data["twda_id"]}`
//     document.getElementById("deck-header").innerHTML = [
//         wrapText(data["player"], 40),
//         wrapText(data["event"], 40),
//         wrapText(data["place"], 40),
//         data["date"],
//         data["players_count"] + " players",
//     ].join("<br/>")
//     document.getElementById("crypt-header").textContent = `Crypt (${data["crypt"]["count"]})`
//     var cards = []
//     data["crypt"]["cards"].forEach((value, index) => { cards.push(cardElement(value, index)) })
//     document.getElementById("crypt-list").innerHTML = cards.join("\n")
//     document.getElementById("library-header").textContent = `Library (${data["library"]["count"]})`
//     var offset = cards.length
//     var cards = new Array()
//     for (const section of data["library"]["cards"]) {
//         cards.push(`<li><h4>— ${section["type"]} (${section["count"]}) —</h4></li>`)
//         section["cards"].forEach((value, index) => { cards.push(cardElement(value, offset + index)) })
//         offset += section["cards"].length
//     }
//     document.getElementById("library-list").innerHTML = cards.join("\n")
//     comments = document.getElementById("comments")
//     for (let section of data["comments"].split("\n\n")) {
//         pelem = document.createElement("p")
//         pelem.textContent = section
//         comments.appendChild(pelem)
//     }
//     document.getElementById("decklist").style.display = "block"
//     document.getElementById("comments-title").style.display = "block"
// }
function displayDeckChoices(data) {
    removeComments()
    let list = ""
    let message = ""
    if (!data || data.length < 1) {
        message = "No result in TWDA."
    } else if (data.length === 1) {
        message = `1 deck found.`
    } else {
        message = `${data.length} decks found.`
    }
    document.getElementById("result-message").innerHTML = `<p>${message}</p>`
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
    document.getElementById("card-modal").addEventListener("keydown", modalKeydown)
    document.getElementById("card-prev").addEventListener("click", prevCard)
    document.getElementById("card-next").addEventListener("click", nextCard)
    autocomplete(document.getElementById("card_name"))
    displayDeckFromURL()
    window.onpopstate = displayDeckFromURL
}
