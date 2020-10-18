function dC(name) {
    document.getElementById("card-image").src = "https://images.krcg.org/".concat(
        name,
        ".jpg"
    )
    document.getElementById("card-prev").style.display = "none"
    document.getElementById("card-next").style.display = "none"
    document.getElementById("card-modal").style.display = "block"
}
function dCi(i) {
    console.log(`dCi ${i}`)
    const card = document.getElementById(`card-${i}`)
    if (!card) {
        return
    }
    var name = card.textContent.toLowerCase()
    if (name.startsWith("the ")) {
        name = name.substr(4, name.length) + "the"
    }
    name = name.replace(/\s|,|\.|-|—|'|:|\(|\)|"|\/|!/g, "")
    name = name.replace(/ö|ó/g, "o") // Rötschreck, Dónal
    name = name.replace(/é|ë|è/g, "e") // Céleste, Gaël, Père
    name = name.replace(/œ/g, "oe") // Cœur
    name = name.replace(/ç/g, "c") // Monçada
    name = name.replace(/á|ã/g, "a") // Vásquez, João
    name = name.replace(/í|î/g, "i") // Día, Maître
    name = name.replace(/ñ/g, "n") // Montaña
    name = name.replace(/ü|ú/g, "u") // Powerbase: Zürich, Jesús
    name = name.replace(/™/g, "tm") // Pentex™
    document.getElementById(`card-image`).src = "https://images.krcg.org/".concat(
        name,
        ".jpg"
    )
    var modal = document.getElementById("card-modal")
    for (const c of modal.classList) {
        if (c.startsWith("modal-card-")) {
            modal.classList.remove(c)
        }
    }
    modal.classList.add(`modal-card-${i}`)
    document.getElementById("card-prev").style.display = "block"
    document.getElementById("card-next").style.display = "block"
    modal.style.display = "block"
    modal.focus()
}
function cardIndex(modal) {
    for (const c of modal.classList) {
        if (c.startsWith("modal-card-")) {
            return parseInt(c.match(/[0-9]+/)[0])
        }
    }
}
function prevCard(event) {
    event.stopPropagation()
    dCi(cardIndex(event.target.parentElement) - 1)
}
function nextCard(event) {
    event.stopPropagation()
    dCi(cardIndex(event.target.parentElement) + 1)
}
function modalKeydown(event) {
    event.stopPropagation()
    event.preventDefault()
    // arrow DOWN
    if (event.keyCode === 40) {
        dCi(cardIndex(event.target) + 1)
        // arrow UP
    } else if (event.keyCode === 38) {
        dCi(cardIndex(event.target) - 1)
    }
}
function cardElement(element, i) {
    const name = element["name"]
    return `<li>${element["count"]} <span class="card" id="card-${i}" onclick="dCi(${i})">${name}</span></li>`
}
function wrapText(text, maxlen) {
    if (!text) {
        //return "(No name)"
		return ""
    }
    if (text.length > maxlen) {
        return text.substr(0, maxlen - 3) + "..."
    }
    return text
}
function removeComments() {
    var comments = document.getElementById("comments")
    if (comments) {
        comments.innerHTML = ""
    }
}
function displayDeck(data) {
    removeComments()
    document.getElementById("deck-link").textContent = wrapText(
        data["name"],
        25
    )
    document.getElementById(
        "deck-link"
    ).href = `http://www.vekn.fr/decks/twd.htm#${data["twda_id"]}`
    document.getElementById("deck-header").innerHTML = [
        wrapText(data["player"], 40),
        wrapText(data["event"], 40),
        wrapText(data["place"], 40),
        data["date"],
        (typeof data["players_count"] == "number") ? data["players_count"] + " players" : "",
    ].join("<br/>")
    document.getElementById(
        "crypt-header"
    ).textContent = `Crypt (${data["crypt"]["count"]})`
    var cards = []
    data["crypt"]["cards"].forEach((value, index) => {
        cards.push(cardElement(value, index))
    })
    document.getElementById("crypt-list").innerHTML = cards.join("\n")
    document.getElementById(
        "library-header"
    ).textContent = `Library (${data["library"]["count"]})`
    var offset = cards.length
    var cards = new Array()
    for (const section of data["library"]["cards"]) {
        cards.push(
            `<li><h4>— ${section["type"]} (${section["count"]}) —</h4></li>`
        )
        section["cards"].forEach((value, index) => {
            cards.push(cardElement(value, offset + index))
        })
        offset += section["cards"].length
    }
    document.getElementById("library-list").innerHTML = cards.join("\n")
    comments = document.getElementById("comments")
    if (comments) {
        for (let section of data["comments"].split("\n\n")) {
            pelem = document.createElement("p")
            pelem.textContent = section
            comments.appendChild(pelem)
        }
        document.getElementById("comments-title").style.display = "block"
    }
    document.getElementById("decklist").style.display = "block"
}
