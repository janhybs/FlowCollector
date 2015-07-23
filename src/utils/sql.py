# encoding: utf-8
# author:   Jan Hybs



insert_condition_fields = ['program-branch', 'program-build', 'timer-resolution',
                           'task-description', 'task-size', 'run-process-count']
insert_condition_query = \
    """
        INSERT INTO  `condition` (
        `id` , `branch` , `build` , `timer_resolution` ,
        `task_name` ,`task_size` , `process_count`
        )
        VALUES (
        NULL ,  %(program-branch)s,  %(program-build)s,  %(timer-resolution)s,
        %(task-description)s,  %(task-size)s,  %(run-process-count)s
        )
    """

insert_structure_query = \
    """
        INSERT INTO  `structure` (
        `name` , `parent`
        )
        VALUES (
        %(name)s, %(parent)s
        );
    """

insert_measurement_query = \
    """
        INSERT INTO  `measurement` (
        `id` , `type` , `value` , `structure` , `cond`
        )
        VALUES (
        NULL ,  %(type)s,  %(value)s,  %(structure)s,  %(cond)s
        )
    """