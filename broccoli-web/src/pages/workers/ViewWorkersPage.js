import React, { Component } from 'react'

export default class ViewWorkersPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      "loading": true,
      "workers": [],
    };

    this.onReplicate = this.onReplicate.bind(this);
    this.onRemove = this.onRemove.bind(this);
    this.onUpdateIntervalSeconds = this.onUpdateIntervalSeconds.bind(this)
  }

  componentDidMount() {
    this.props.workerManagerClient.getWorkers()
      .then(response => {
        const workers = response.data;
        this.setState({
          "loading": false,
          "workers": workers.map(worker => {
            return {
              ...worker,
              "state": "Loading...",
              "lastSeen": 0,
              "metadata": ""
            }
          })
        });
        return Promise.all(workers.map(worker => this.props.workerManagerClient.getWorkerEvents(
          worker["worker_id"], undefined, undefined, 1
        )))
      })
      .then(allLatestEvents => {
        this.setState({
          "workers": this.state.workers.map((worker, index) => {
            const latestEvents = allLatestEvents[index].data;
            if (latestEvents.length === 0) {
              return {
                ...worker,
                "state": "N/A",
                "lastSeen": 0,
                "metadata": "N/A"
              }
            } else {
              const {state, timestamp, metadata} = latestEvents[0];
              let metadataStr = "";
              if (state === "FINISHED") {
                metadataStr = `Runtime ${metadata["run_time_nanoseconds"] / 1e6} milliseconds`
              } else if (state === "ERRORED") {
                metadataStr = `Exception ${metadata["exception"]}`
              }
              return {
                ...worker,
                "state": state,
                "lastSeen": (Date.now() - timestamp) / 1000,
                "metadata": metadataStr
              }
            }
          })
        })
      })
  }

  onReplicate(e, module, className, args, globalArgs, intervalSeconds) {
    this.replicate(module, className, args, globalArgs, intervalSeconds);
    e.preventDefault()
  }

  replicate(module, className, args, globalArgs, intervalSeconds) {
    this.props.redirectTo(
      `/workers/create?module=${module}&class_name=${className}&args=${encodeURIComponent(JSON.stringify(args))}&global_args=${encodeURIComponent(JSON.stringify(globalArgs))}&interval_seconds=${intervalSeconds}`
    )
  }

  onRemove(e, workerId) {
    this.remove(workerId);
    e.preventDefault()
  }

  remove(workerId) {
    if (window.confirm(`Are you sure you want to remove worker ${workerId}`)) {
      this.props.workerManagerClient.removeWorker(workerId)
        .then(() => {
          this.setState({
            ...this.state,
            "workers": this.state.workers.filter(worker => worker["worker_id"] !== workerId),
          });
          this.props.showOkMessage(`Removed worker ${workerId}`)
        })
        .catch(error => {
          console.error(error.response.data);
          this.props.showErrorMessage(JSON.stringify(error.response.data))
        });
    }
  }

  onUpdateIntervalSeconds(e, workerId, intervalSeconds) {
    this.updateIntervalSeconds(workerId, intervalSeconds);
    e.preventDefault()
  }

  updateIntervalSeconds(workerId, intervalSeconds) {
    this.props.workerManagerClient.updateWorkerIntervalSeconds(workerId, intervalSeconds)
      .then(() => {

        this.props.showOkMessage(`Updated worker ${workerId} with interval seconds ${intervalSeconds}`)
      })
      .catch(error => {
        console.error(error.response.data);
        this.props.showErrorMessage(JSON.stringify(error.response.data))
      });
  }

  renderWorkersTable(workers) {
    return (
      <table>
        <thead>
        <tr>
          <th>ID</th>
          <th>Module</th>
          <th>Class Name</th>
          <th>Args</th>
          <th>Global Args</th>
          <th>Interval (seconds)</th>
          <th>State</th>
          <th>Last Seen (seconds)</th>
          <th>Metadata</th>
          <th>Operations</th>
        </tr>
        </thead>
        <tbody>
        {
          workers.map(worker => {
            const {
              "worker_id": workerId,
              module,
              "class_name": className,
              args,
              "global_args": globalArgs,
              "interval_seconds": intervalSeconds,
              state,
              lastSeen,
              metadata
            } = worker;
            return (
              <tr key={workerId}>
                <td>{workerId}</td>
                <td>{module}</td>
                <td>{className}</td>
                <td>{JSON.stringify(args)}</td>
                <td>{JSON.stringify(globalArgs)}</td>
                <td>
                  <input type="number" value={intervalSeconds} onChange={e => {
                    this.setState({
                      "workers": this.state.workers.map(worker => {
                        if (worker["worker_id"] !== workerId) {
                          return worker
                        }
                        return {
                          ...worker,
                          "interval_seconds": parseInt(e.target.value)
                        }
                      })
                    })
                  }}/>
                  <button onClick={e => {this.onUpdateIntervalSeconds(e, workerId, intervalSeconds)}}>Update</button>
                </td>
                <td>{state}</td>
                <td>{lastSeen}</td>
                <td>{metadata}</td>
                <td>
                  <button onClick={e => this.onReplicate(e, module, className, args, globalArgs, intervalSeconds)}>Create from</button>
                  <button onClick={e => this.onRemove(e, workerId)}>x</button>
                </td>
              </tr>
            )
          })
        }
        </tbody>
      </table>
    )
  }

  render() {
    return (
      <div>
        <b>View workers</b>
        { this.state.loading ? <div>Loading workers...</div> : this.renderWorkersTable(this.state["workers"]) }
      </div>
    )
  }
}
