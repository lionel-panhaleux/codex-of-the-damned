function get_cardLink(card) {
    var origin = window.location.origin
    var pathname = window.location.pathname
    pathname = pathname.substr(0, 4)
    pathname = pathname + "card-search.html?card="
    pathname = origin + pathname
    card = card.replaceAll(" ", "+")
    return pathname + card
}

function create_link() {
    let link = document.createElement("a")
    link.id = "krcg-tag-link"
    link.target = "_blank"
    link.classList.add("hyperlink-button")
    let see_more = document.createElement("p")
    see_more.id = "krcg-modal-link"
    see_more.classList.add("krcg-modal-link")
    see_more.append(link)
    document.getElementById('krcg-click-image').after(see_more)
}

function link_text() {
    let lang = window.location.pathname.slice(1, 3)
    if (lang == "fr") return "En savoir plus"
    if (lang == "es") return "Más información"
    return "See more about it"
}

function serve_link(card) {
    let link = document.getElementById("krcg-tag-link")
    link.innerHTML = link_text()
    link.href = get_cardLink(getName(card))
}

function extends_clickCard() {
    if (document.getElementById("krcg-tag-link")) {
        serve_link(this)
    } else {
        create_link()
        serve_link(this)
    }
}

window.addEventListener("load", (e) => {
    // add new event listener on all page elements marked as cards
    for (elem of document.querySelectorAll(".krcg-card")) {
        elem.addEventListener("click", extends_clickCard.bind(elem))
    }
})
