import React, {useState} from "react";
function ProgressBar({totalUpdates, currentUpdate}) {
    // Percentage between 0 and 100; Once 100% is reached, flashcard download starts.
    const progress = currentUpdate / totalUpdates * 100

    return (
      <div className="progress-bar-container">
          <div className="progress-bar">
                <div className="progress-bar-inner">
                    <div className="progress-bar-progress" style={{width: `${progress}%`}}>
                    </div>
                </div>
          </div>
      </div>
    );
}

export default ProgressBar;