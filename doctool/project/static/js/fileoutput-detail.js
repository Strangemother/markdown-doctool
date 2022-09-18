

const toggleView = function(label, classStr) {
    console.log('toggleView', label)
    classStr = classStr == undefined? label: classStr;
    let nodes = document.querySelectorAll(`.toggleview-${label}`)
    nodes.forEach(n=>n.classList.toggle(classStr))
}
