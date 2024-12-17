"""Response-time analysis for global fixed-priority scheduling according
to Guan et al., "New Response Time Bounds for Fixed Priority
Multiprocessor Scheduling", published at RTSS'09

Note: this implementation covers only the constrained-deadline case.
"""



from __future__ import division

from math import ceil, floor
# from itertools import izip

try:
    xrange
except NameError:
    xrange = range


def is_schedulable(num_cpus, tasks):
    return all(rta_schedulable_guan(k, tasks, num_cpus) for k in xrange(len(tasks)))


bound_response_times = is_schedulable


def is_schedulable_rta_lc_quan_2017(num_cpus, tasks):
    omegalist = {}
    ret = all(rta_schedulable_guan(k, tasks, num_cpus, 'rta-lc-quan-2017', omegalist) for k in xrange(len(tasks)))
    print(omegalist)
    return ret

def is_schedulable_rta_lc(num_cpus, tasks):
    ret = all(rta_schedulable_guan(k, tasks, num_cpus,  'rta-lc') for k in xrange(len(tasks)))
    
    return ret
    # return rta_schedulable_guan(a,b,c,)

def is_schedulable_c_rta(num_cpus, tasks):
    return all(rta_schedulable_guan(k, tasks, num_cpus, 'c-rta') for k in xrange(len(tasks)))

def is_schedulable_d_rta(num_cpus, tasks):
    return all(rta_schedulable_guan(k, tasks, num_cpus, 'd-rta') for k in xrange(len(tasks)))


#
# Task t_k is the task under analysis.
#
def rta_schedulable_guan(k, taskset, num_cpus,  rtatype='rta-lc', omegalist=None):
    "Assumes k = index = priority"
    #Use Guan et al.'s response-time analysis
    #in RTSS 2009 (an extension of Baruah's RTSS'07 paper)
    tk = taskset[k]
    

    assert tk.deadline <= tk.period # only constrained deadlines covered

    if k < num_cpus:
        if tk.cost > tk.deadline:
            return False
        else:
            tk.response_time = tk.cost
            return True

    test_end = tk.deadline
    time = tk.cost
    while time <= test_end:
        #Eq. 12 in Guan's RTSS'09 paper
        interference = total_interference(k, taskset, num_cpus, time, omegalist, rtatype)
        # if tk not in omegalist.keys():
        #     kk = dict()            
        # else:
        #     kk = omegalist[tk]

        # kk[time]= interference
        # omegalist[tk] = kk


        # omegalist[k] = {time:interference}

        # print('omega list k={}, time={}, omega={} '.format(k, time, interference))
        # print(omegalist)

        interference = int(floor(interference  / num_cpus))

        demand = tk.cost + interference

        if demand == time:
            # demand will be met by time
            tk.response_time = time
            # print "OK", k,"rta", demand,time
            return True
        else:
            # try again            
            time = demand
    
    tk.response_time = time
    # print ("NOK", k,"rta", demand,time)

    return False

# def rta_lc_quan_2017_mini(ti, x, omegalist, m ):
#     # return 0
#     # Quan 2017 lema 1
#     # mini = [ min(ti.cost, max(0, y - floor(omegalist[ti][y]/m))) for y in xrange(1, x+1)]
#     print('rta_lc_quan_2017_mini', x)
#     mini = []
#     for y in xrange(1, x+1):
#         print('rta_lc_quan_2017_mini', ti, y, omegalist[ti][y])
#         tmp = y - floor(omegalist[ti][y]/m)

#         tmp1 = min(ti.cost, max(0, tmp1))
#         mini += tmp1

#     return max(mini)

# def rta_lc_quan_2017_maxi(ti, x, omegalist, num_cpus):
#     # return 0
#     print('rta_lc_quan_2017_maxi', x)
#     maxi = ti.cost - rta_lc_quan_2017_mini(ti, ti.period - x, omegalist, num_cpus)
#     return maxi

#carry-in interference of task "task" during an interval of
#length "time", based on Eq. 6 and Eq. 8 in Guan's RTSS'09 paper
def interference_with_carry_in(ti, tk, time, omegalist, num_cpus, rtatype):
    #Eq. 6 in Guan's RTSS'09 paper
    #alpha = [[x - Ci]_0 mod Ti - (Ti - Ri)]_0^Ci-1
    # if rtatype=='rta-lc-quan-2017':
    #     # Quan 2017 eq. 20
    #     gama = max(0,  time - ti.cost ) % ti.period 
    #     beta = min( max(0, rta_lc_quan_2017_maxi(ti, gama, omegalist, num_cpus)), ti.cost - 1)
    #     alpha = beta
    
    if rtatype=='rta-lc':
        alpha_tmp = max(0,  time - ti.cost ) % ti.period - (ti.period - ti.response_time)
        alpha = min(max( alpha_tmp, 0 ), ti.cost - 1)

    elif rtatype=='c-rta':
        alpha_tmp = max(0,  time - ti.cost ) % ti.period - (ti.period - ti.cost)
        alpha = min(max( alpha_tmp, 0 ), ti.cost - 1)

    elif rtatype=='d-rta':
        alpha_tmp = max(0,  time - ti.cost ) % ti.period - (ti.period - ti.deadline)
        alpha = min(max( alpha_tmp, 0 ), ti.cost - 1)

    

    #Wk^{CI}(ti, x) = lfloor [x - Ci]_0 / Ti  rfloor * Ci + Ci + alpha
    wk_ci = floor(max(time - ti.cost, 0) / ti.period) * ti.cost + ti.cost + alpha

    #Eq. 8 in Guan's RTSS'09 paper
    #[ Wk^{CI}(ti, x) ]_0^{x - Ck + 1}
    ik_ci = min(max(wk_ci, 0), time - tk.cost + 1)

    return ik_ci

#non-carry-in interference of task "task" during an interval of
#length "time", based on Eq. 5 and Eq. 7 in Guan's RTSS'09 paper
def interference_without_carry_in(ti, tk, time):
    #Eq. 5 in Guan's RTSS'09 paper
    #Wk^{NC}(ti, x) = lfloor x / Ti rfloor * Ci + [x mod Ti]^{Ci}
    wk_nc = floor(time / ti.period) * ti.cost + min(time % ti.period, ti.cost)

    #Eq. 7 in Guan's RTSS'09 paper
    #[ Wk^{NC}(ti, x) ]_0^{x - Ck + 1}
    ik_nc = min(max(wk_nc, 0), time - tk.cost + 1)

    return ik_nc

#The total interference Omega_k(x), in Eq. 9 in Guan's RTSS'09 paper
def total_interference(k, taskset, num_cpus, time, omegalist, rtatype):
    tk = taskset[k]
    higher_prio = taskset[:k]

    # compute higher-prio interference without carry-in
    interf_nc = [interference_without_carry_in(ti, tk, time)
                 for ti in higher_prio]

    # the difference of each higher-priority task's carry-in interference and
    # non-carry-in interference
    # calculate the difference of carry-in interference and non-carry-in interference
    # corresponds to Eq. 6 in Baruah's RTSS'07 paper
    idiff = [interference_with_carry_in(ti, tk, time, omegalist, num_cpus, rtatype) - inc
    # idiff = [interference_without_carry_in(ti, tk, time+ti.response_time-ti.cost) - inc
             for (ti, inc) in zip(higher_prio, interf_nc)]
    # All HP tasks are partitioned into tau_NC and tau_CI for use
    # in Eq. 9 in Guan's RTSS'09 paper. For tau_CI, we select the m-1
    # tasks with the maximal difference.
    idiff.sort(reverse=True)
    num_carry_in = num_cpus - 1
    omega = sum(idiff[:num_carry_in])

    # Omega_k(x) can be bounded according to Theorem 2 in Baruah's RTSS'07 paper
    # Omega_k(x)= sum_dif + sum_{i<k} ik_nc
    # add the interference for no-carry-in for ALL tasks, tau_CI and tau_NC
    omega += sum(interf_nc)

    # We added the no-carry-in interference for all tasks, and the difference
    # for all tasks in tau_CI. Overall, omega is the sum of
    # no-carry-in-interference for tasks in tau_NC, and
    # carry-in-interference for tasks in tau_CI.
    # print("omega(tk {}, {}, time {} " .format(k, tk, time))
    return omega


def is_schedulable_da_lc(num_cpus, tasks):
    return all(da_lc_schedulable_guan(k, tasks, num_cpus) for k in xrange(len(tasks)))

def da_lc_schedulable_guan(k, taskset, num_cpus):
    "Assumes k = index = priority"
    #Use Guan et al.'s response-time analysis
    #in RTSS 2009 (an extension of Baruah's RTSS'07 paper)
    tk = taskset[k]    

    assert tk.deadline <= tk.period # only constrained deadlines covered

    if k < num_cpus:
        if tk.cost > tk.deadline:
            return False
        else:
            tk.response_time = tk.cost
            return True

    for ti in taskset:
        ti.response_time = tk.deadline

    interference = total_interference(k, taskset, num_cpus, tk.deadline, [], "rta-lc")
    interference = int(floor(interference  / num_cpus))
    demand = tk.cost + interference

    if demand <= tk.deadline:
        # print ("OK  DA-LC", "task:", k," deadline", tk.deadline, "demand ", demand)
        return True
    else:
        # print ("NOK  DA-LC", "task:", k," deadline", tk.deadline, "demand ", demand)
        return False



if __name__ == "__main__":    
    
    # from ... import model    
    from rtmodel import tasks
    from schedule import rta_lc_guan09 as rtalc
    
    m = 2

    ts = tasks.TaskSystem([
        tasks.SporadicTask(1,  4),
        tasks.SporadicTask(1,  5),    
        tasks.SporadicTask(11, 18),    
        tasks.SporadicTask(6,  9),
    ])
    ts.sort_by_deadline()
    b = rtalc.is_schedulable_rta_lc(m, ts)
    print("rta lc", b)
    b = rtalc.is_schedulable_c_rta(m, ts)
    print("c-rta lc", b)

    b = rtalc.is_schedulable_d_rta(m, ts)
    print("d-rta lc", b)

    b = audsley_opa(ts, m, lambda x: rtalc.is_schedulable_da_lc(m, x))
    print ("audsley_opa", b, ts)