# Copyright (c) 2015, NVIDIA CORPORATION.  All rights reserved.

import flask

from digits.utils.routing import request_wants_json, job_from_request
from digits.webapp import app, scheduler, autodoc
from digits.dataset import tasks
from forms import GenericImageDatasetForm
from job import GenericImageDatasetJob

NAMESPACE = '/datasets/images/generic'

@app.route(NAMESPACE + '/new', methods=['GET'])
@autodoc('datasets')
def generic_image_dataset_new():
    """
    Returns a form for a new GenericImageDatasetJob
    """
    form = GenericImageDatasetForm()
    return flask.render_template('datasets/images/generic/new.html', form=form)

@app.route(NAMESPACE + '.json', methods=['POST'])
@app.route(NAMESPACE, methods=['POST'])
@autodoc(['datasets', 'api'])
def generic_image_dataset_create():
    """
    Creates a new GenericImageDatasetJob

    Returns JSON when requested: {job_id,name,status} or {errors:[]}
    """
    form = GenericImageDatasetForm()
    if not form.validate_on_submit():
        if request_wants_json():
            return flask.jsonify({'errors': form.errors}), 400
        else:
            return flask.render_template('datasets/images/generic/new.html', form=form), 400

    job = None
    try:
        job = GenericImageDatasetJob(
                name = form.dataset_name.data,
                mean_file = form.prebuilt_mean_file.data.strip(),
                )

        if form.method.data == 'prebuilt':
            pass
        else:
            raise ValueError('method not supported')

        force_same_shape = form.force_same_shape.data

        job.tasks.append(
                tasks.AnalyzeDbTask(
                    job_dir     = job.dir(),
                    database    = form.prebuilt_train_images.data,
                    purpose     = form.prebuilt_train_images.label.text,
                    force_same_shape = force_same_shape,
                    )
                )

        if form.prebuilt_train_labels.data:
            job.tasks.append(
                    tasks.AnalyzeDbTask(
                        job_dir     = job.dir(),
                        database    = form.prebuilt_train_labels.data,
                        purpose     = form.prebuilt_train_labels.label.text,
                        force_same_shape = force_same_shape,
                        )
                    )

        if form.prebuilt_val_images.data:
            job.tasks.append(
                    tasks.AnalyzeDbTask(
                        job_dir     = job.dir(),
                        database    = form.prebuilt_val_images.data,
                        purpose     = form.prebuilt_val_images.label.text,
                        force_same_shape = force_same_shape,
                        )
                    )
            if form.prebuilt_val_labels.data:
                job.tasks.append(
                        tasks.AnalyzeDbTask(
                            job_dir     = job.dir(),
                            database    = form.prebuilt_val_labels.data,
                            purpose     = form.prebuilt_val_labels.label.text,
                            force_same_shape = force_same_shape,
                            )
                        )

        scheduler.add_job(job)

        if request_wants_json():
            return flask.jsonify(job.json_dict())
        else:
            return flask.redirect(flask.url_for('datasets_show', job_id=job.id()))

    except:
        if job:
            scheduler.delete_job(job)
        raise

def show(job):
    """
    Called from digits.dataset.views.datasets_show()
    """
    return flask.render_template('datasets/images/generic/show.html', job=job)

@app.route(NAMESPACE + '/summary', methods=['GET'])
@autodoc('datasets')
def generic_image_dataset_summary():
    """
    Return a short HTML summary of a DatasetJob
    """
    job = job_from_request()

    return flask.render_template('datasets/images/generic/summary.html', dataset=job)
