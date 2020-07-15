import React, { Component } from 'react'
import { Link } from "react-router-dom"

export default class ViewWorkersPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      "loading": true,
      "workers": [],
    };
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

  onReplicate = (module, className, args, intervalSeconds) => {
    this.props.redirectTo(
      `/workers/create?module=${module}&class_name=${className}&args=${encodeURIComponent(JSON.stringify(args))}&interval_seconds=${intervalSeconds}`
    )
  }

  onRemove = workerId => {
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

  onUpdateIntervalSeconds = (workerId, intervalSeconds) => {
    this.props.apiClient.updateWorkerIntervalSeconds(workerId, intervalSeconds)
      .then(() => {
        this.props.showOkMessage(`Updated worker ${workerId} with interval seconds ${intervalSeconds}`)
      })
      .catch(error => {
        console.error(error.response.data);
        this.props.showErrorMessage(JSON.stringify(error.response.data))
      });
  }

  onUpdateErrorResiliency = (workerId, errorResiliency) => {
    this.props.apiClient.updateWorkerErrorResiliency(workerId, errorResiliency)
      .then(() => {
        this.props.showOkMessage(`Updated worker ${workerId} with error resiliency ${errorResiliency}`)
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
          <th>Interval (seconds)</th>
          <th>Error Resiliency (non-positive is none)</th>
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
                <td>
                  <input type="number" value={intervalSeconds} onChange={e => {
                    e.preventDefault();
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
                  <button onClick={e => {
                    e.preventDefault()
                    this.onUpdateIntervalSeconds(workerId, intervalSeconds)}
                  }>Update</button>
                </td>
                <td>
                  <input type="number" min={-1} value={errorResiliency} onChange={e => {
                    e.preventDefault();
                    this.setState({
                      "workers": this.state.workers.map(worker => {
                        if (worker["worker_id"] !== workerId) {
                          return worker
                        }
                        return {
                          ...worker,
                          "error_resiliency": parseInt(e.target.value)
                        }
                      })
                    })
                  }}/>
                  <button onClick={e => {
                    e.preventDefault()
                    this.onUpdateErrorResiliency(workerId, errorResiliency)}
                  }>Update</button>
                </td>
                <td>{executorSlug}</td>
                <td>
                  <button onClick={e => {
                    e.preventDefault();
                    this.onReplicate(module, className, args, intervalSeconds)
                  }}>Create from</button>
                  <button onClick={e => {
                    e.preventDefault();
                    this.onRemove(workerId)
                  }}>x</button>
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
