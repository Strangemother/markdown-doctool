window.addEventListener("load", () => {
    // Retrieve all help sections
    let selection = 'h1,h2,h3,h4,h5,h6'
    const headers = Array.from(document.querySelectorAll(selection));

    // Once a scrolling event is detected, iterate all elements
    // whose visibility changed and highlight their navigation entry
    const scrollHandler = entries =>
        entries.forEach(entry => {
            const section = entry.target;
            const sectionId = section.id;
            const sectionLink = document.querySelector(`a[href="#${sectionId}"]`);
            if(sectionLink == null) {
                console.log('No section link for', entry.target, sectionId)
                return
            }
            if (entry.intersectionRatio > 0) {
                section.classList.add("visible");
                sectionLink.classList.add("visible");
            } else {
                section.classList.remove("visible");
                sectionLink.classList.remove("visible");
            }
        }
    );

    // Creates a new scroll observer
    const observer = new IntersectionObserver(scrollHandler);

    //noinspection JSCheckFunctionSignatures
    headers.forEach(section => observer.observe(section));
});

