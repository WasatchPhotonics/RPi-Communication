import SpectraChart from './components/Chart';
import './App.css';

function App() {
  return (
    <div className="App">
          <div className="pageWindow">
            <SpectraChart />
            <ControlWidget />
          </div>
    </div>
  );
}

export default App;
