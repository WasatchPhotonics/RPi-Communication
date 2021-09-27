import SpectraChart from './Chart';
import Marquee from './Marquee'
import '../../App.css';

function ScopePage(props) {


    return (
        <div className="displayWindow">
            <Marquee />
            <div className="pageWindow">
                <SpectraChart spectraValues={props.spectraValues}
                    spectraStats={props.spectraStats}
                    xUnits={props.xUnits}
                    markers={props.markers}
                    reverseAxis={props.reverseAxis}/>
            </div>
        </div>
    );
}

export default ScopePage;