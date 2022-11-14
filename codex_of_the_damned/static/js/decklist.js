function wrapText(text, maxlen) {
    if (!text) {
        return "(N/A)"
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
function addCard(section, card_info) {
    let elem = document.createElement("li")
    elem.textContent = `${card_info.count} `
    let card = document.createElement("span")
    card.textContent = card_info.name
    card.classList.add("krcg-card")
    card.addEventListener("click", clickCard.bind(card))
    card.addEventListener("mouseover", overCard.bind(card))
    card.addEventListener("mouseout", outCard)
    elem.appendChild(card)
    section.appendChild(elem)
}
function VdbDeckInUrl(data) {
    let res = "https://vdb.im/decks/deck?"
    if (data.name) {
        res += `name=${encodeURIComponent((data.name))}`
    }
    res += "#"
    for (card of data.crypt.cards) {
        res += `${card.id}=${card.count};`
    }
    for (const section of data.library.cards) {
        for (card of section.cards) {
            res += `${card.id}=${card.count};`
        }
    }
    return res.slice(0, -1)
}
function displayDeck(data, deckname = undefined) {
    removeComments()
    document.getElementById("deck-link").textContent = wrapText(deckname || data.name || "(No Name)", 25)
    let vdb_button = document.getElementById("vdb-button")
    if (data.id) {
        document.getElementById("deck-link").setAttribute("href", `https://static.krcg.org/data/twd.htm#${data.id}`)
        if (vdb_button) {
            vdb_button.setAttribute("href", `https://vdb.im/decks?id=${data.id}`)
            vdb_button.style.display = "block"
        }
    } else {
        if (data.link) {
            document.getElementById("deck-link").setAttribute("href", data.link)
        }
        else {
            document.getElementById("deck-link").removeAttribute("href")
        }
        if (vdb_button) {
            vdb_button.setAttribute("href", VdbDeckInUrl(data))
            vdb_button.style.display = "block"
        }
    }
    header_lines = []
    if (data.player || data.author) {
        header_lines.push(wrapText(data.player || data.author, 40))
    }
    if (data.event) {
        header_lines.push(wrapText(data.event, 40))
    }
    if (data.place) {
        header_lines.push(wrapText(data.place, 40))
    }
    if (data.date) {
        header_lines.push(wrapText(data.date, 40))
    }
    if (data.players_count) {
        header_lines.push(wrapText(data.players_count, 32) + " players")
    }
    document.getElementById("deck-header").innerHTML = header_lines.join("<br>")
    document.getElementById("crypt-header").textContent = `Crypt (${data.crypt.count})`
    let crypt = document.getElementById("crypt-list")
    crypt.innerHTML = ""
    for (card_info of data.crypt.cards) {
        addCard(crypt, card_info)
    }
    document.getElementById("library-header").textContent = `Library (${data.library.count})`
    let library = document.getElementById("library-list")
    library.innerHTML = ""
    for (const section of data.library.cards) {
        let header = document.createElement("li")
        let title = document.createElement("h4")
        title.textContent = `— ${section.type} (${section.count}) —`
        header.appendChild(title)
        library.appendChild(header)
        for (card_info of section.cards) {
            addCard(library, card_info)
        }
    }
    comments = document.getElementById("comments")
    if (comments && data.comments) {
        for (const section of data.comments.split("\n\n")) {
            pelem = document.createElement("p")
            pelem.textContent = section
            comments.appendChild(pelem)
        }
        document.getElementById("comments-title").style.display = "block"
    }
    document.getElementById("decklist").style.display = "block"
}
window.addEventListener("load", function () {
    let content = document.querySelector('meta[property="decklist"]')
    if (!content) {
        return
    }
    content = content.content
    const decklist = JSON.parse(JSON.parse(content))
    displayDeck(decklist)
})
