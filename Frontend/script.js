function login(username, password) {
    return fetch("http://localhost:8000/users/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => response.json())
    .catch(error => {
        console.log(error);
        throw error;
    });
}

function retrieveBooks(token, start, end) {
    return fetch(`http://localhost:8000/books?start=${start}&end=${end}`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    })
    .then(response => response.json())
    .catch(error => {
        console.log(error);
        throw error;
    });
}

function updatePage(books) {
    let book_gallery = document.getElementById("book-display");
    book_gallery.innerHTML = '';
    books.forEach(book => {
        let book_element = document.createElement("div");
        book_element.classList = "book";
        alt = "images/generic_book_cover.png"
        book_element.innerHTML = `
            <img class="book-img" src="${book.thumbnail}" alt="Book Cover" onerror="this.src='${alt}'">
            <div class="book-title">${book.title}</div>
        `;
        book_gallery.appendChild(book_element);
    });
}

function setupPagination(token, totalBooks, per_page, currentPage = 1) {
    const totalPages = Math.ceil(totalBooks / per_page);
    const paginationContainer = document.getElementById("page-buttons");
    paginationContainer.innerHTML = '';

    const endPage = currentPage > 2 ? currentPage + 2 : 5;
    const startPage = currentPage > 2 ? currentPage - 2 : 1;

    console.log(endPage, startPage)

    for (let i = startPage; i <= endPage; i++) {
        const pageButton = document.createElement("button");
        pageButton.className = "page-button";
        pageButton.innerText = i;
        pageButton.addEventListener("click", () => {
            const start = (i - 1) * per_page + 1;
            const end = i * per_page + 1;
            retrieveBooks(token, start, end).then(response => {
                if (response && response.books) {
                    updatePage(response.books);
                    setupPagination(token, totalBooks, per_page, i); 
                }
            });
        });
        paginationContainer.appendChild(pageButton);
    }
}

window.onload = (event) => {
    const per_page = 12;
    login("email_0@gmail.com", "password_0")
    .then(response => {
        if (response.access_token) {
            const start = 0;
            const end = per_page;
            return retrieveBooks(response.access_token, start, end).then(booksResponse => {
                if (booksResponse && booksResponse.books) {
                    updatePage(booksResponse.books);
                    const totalBooks = 6180; 
                    setupPagination(response.access_token, totalBooks, per_page);
                }
            });
        } else {
            console.log("Login failed:", response);
        }
    })
    .catch(error => {
        console.log("Error during login or fetching books:", error);
    });
};
