import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faFileArrowUp} from "@fortawesome/free-solid-svg-icons";
import React from "react";

function PDFUploadField({}) {
    return (
        <div className="PDF-upload-field">
            <div className="PDF-placeholder">
                <p>Document uploading coming soon...</p>
                <FontAwesomeIcon icon={faFileArrowUp} className="PDF-upload-icon"/>
            </div>
        </div>
    );
}

export default PDFUploadField;