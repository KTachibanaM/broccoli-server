import React, { Component } from 'react'
import { Link } from "react-router-dom"

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
    this.props.apiClient.getWorkers()
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
        })
      })
  }

  onReplicate(e, module, className, args, intervalSeconds) {
    this.replicate(module, className, args, intervalSeconds);
    e.preventDefault()
  }

  replicate(module, className, args, intervalSeconds) {
    this.props.redirectTo(
      `/workers/create?module=${module}&class_name=${className}&args=${encodeURIComponent(JSON.stringify(args))}&interval_seconds=${intervalSeconds}`
    )
  }

  onRemove(e, workerId) {
    this.remove(workerId);
    e.preventDefault()
  }

  remove(workerId) {
    if (window.confirm(`Are you sure you want to remove worker ${workerId}`)) {
      this.props.apiClient.removeWorker(workerId)
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
    this.props.apiClient.updateWorkerIntervalSeconds(workerId, intervalSeconds)
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
          <th>Interval (seconds)</th>
          <th>Error Resiliency</th>
          <th>Executor Slug</th>
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
              "interval_seconds": intervalSeconds,
              "error_resiliency": errorResiliency,
              "executor_slug": executorSlug
            } = worker;
            return (
              <tr key={workerId}>
                <td>
                  <Link to={`/worker/${workerId}`}>{workerId}</Link>
                </td>
                <td>{module}</td>
                <td>{className}</td>
                <td>{JSON.stringify(args)}</td>
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
                <td>{errorResiliency !== -1 ? errorResiliency : 'N/A'}</td>
                <td>{executorSlug}</td>
                <td>
                  <button onClick={e => this.onReplicate(e, module, className, args, intervalSeconds)}>Create from</button>
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
