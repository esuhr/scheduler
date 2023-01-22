function deleteNote(noteId) {
    fetch("/delete-note", {
        method: "POST",
        body: JSON.stringify({ noteId: noteId})
    }).then((_res) => {
        window.location.href = "/";
    });   
}


function deleteStudent(studentId) {
    fetch("/delete-student", {
        method: "POST",
        body: JSON.stringify({ studentId: studentId})
    }).then((_res) => {
        window.location.href = "/student";
    });   
}

function deleteLesson(lessonId) {
    fetch("/delete-lesson", {
        method: "POST",
        body: JSON.stringify({ lessonId: lessonId})
    }).then((_res) => {
        window.location.href = "/schedule";
    });   
}

function selectElementContents(el) {
    var body = document.body, range, sel;
    if (document.createRange && window.getSelection) {
        range = document.createRange();
        sel = window.getSelection();
        sel.removeAllRanges();
        try {
            range.selectNodeContents(el);
            sel.addRange(range);
        } catch (e) {
            range.selectNode(el);
            sel.addRange(range);
        }
        document.execCommand("Copy");

    } else if (body.createTextRange) {
        range = body.createTextRange();
        range.moveToElementText(el);
        range.select();
        range.execCommand("Copy");
    }
}