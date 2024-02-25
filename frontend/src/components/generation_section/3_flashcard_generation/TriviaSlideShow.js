function TriviaSlideShow() {
    // Slide show to display trivia and fun facts while user waits during flashcard generation

    const renderSlideShow = () => {
        return (
            <div></div>
        );
    }

    return (
        <div className="trivia_show_container">
            <h3>Did you know that...</h3>
            {renderSlideShow()}
        </div>
    );
}

export default TriviaSlideShow;