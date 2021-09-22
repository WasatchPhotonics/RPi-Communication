import SpectraChart from './Chart';
import Marquee from './Marquee'
import ControlWidget from './ControlWidget'
import '../../App.css';

function ScopePage() {
    return (
        <div>
            <Marquee />
            <div className="pageWindow">
                <SpectraChart />
                <ControlWidget />
            </div>
        </div>
    );
}

export default ScopePage;