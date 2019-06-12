// Create the style classes
const styleEl = document.createElement("style");
document.head.appendChild(styleEl);

styleEl.insertAdjacentHTML("beforeend", `
.redClass {
  background-color: red;
  font-weight : bold;
}
.greenClass {
    background-color : green;
    font-weight : bold
}
`);

// Query for the table tags and coloring to the table
const tableElm = document.getElementsByTagName("table")[0]; 
for (const row of tableElm.rows) {
  const childToStyle = row.children[1];
  console.log(childToStyle.textContent);
  if (Number(childToStyle.textContent) < 300) { 
    childToStyle.classList.add("redClass");
  } else if (Number(childToStyle.textContent) > 299) {
      childToStyle.classList.add("greenClass")
  }
}



