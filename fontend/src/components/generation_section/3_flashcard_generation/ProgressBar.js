import React, {useState} from "react";
function ProgressBar({progress}) {
    // Percentage between 0 and 100; Once 100% is reached, flashcard download starts.

    return (
      <div className="progress-bar-container">
          <div className="progress-bar-outer">
                <div className="progress-bar-inner">
                    <div className="progress-bar-progress" style={{width: `${progress}%`}}>
                    </div>
                </div>
          </div>
      </div>
    );
}

export default ProgressBar;