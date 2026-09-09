import URLForm from "../components/URLForm";
import Navbar from "../components/Navbar";

function Home() {
    return (
        <div>
        <Navbar />
        <div className="home">
            <div className="hero">
                <h1>Shorten Your URLs</h1>

                <p>
                    Create short, simple and shareable links in seconds.
                </p>

                <URLForm />
            </div>
        </div>
        </div>
    );
}

export default Home;